import json
import os
from unittest.mock import MagicMock, patch

import requests
from django.test import Client, TestCase
from django.urls import reverse

from ai_services.gemini import (
    APITimeoutError,
    GeminiClient,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    QuotaExceededError,
    _scrub_secret,
)
from contact.models import ContactMessage
from intelligence.models import AISettings
from nexus.models import ChatUsageLog
from nexus.prompts import build_nexus_system_prompt
from portfolio.models import Profile


class GeminiClientUnitTests(TestCase):
    def test_missing_api_key_raises_cleanly(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}, clear=False):
            client = GeminiClient(api_key='')
            with self.assertRaises(MissingAPIKeyError):
                client.generate_chat_reply("sys", [], "hello")

    @patch('ai_services.gemini.requests.post')
    def test_invalid_api_key_handling(self, mock_post):
        resp = MagicMock()
        resp.status_code = 400
        resp.json.return_value = {'error': {'message': 'API key not valid. Please pass a valid API key.'}}
        mock_post.return_value = resp

        client = GeminiClient(api_key='bad-key-123')
        with self.assertRaises(InvalidAPIKeyError):
            client.generate_chat_reply("sys", [], "hello")

    @patch('ai_services.gemini.requests.post')
    def test_quota_exceeded_handling(self, mock_post):
        resp = MagicMock()
        resp.status_code = 429
        resp.json.return_value = {'error': {'message': 'Resource exhausted (429)'}}
        mock_post.return_value = resp

        client = GeminiClient(api_key='valid-test-key')
        with self.assertRaises(QuotaExceededError):
            client.generate_chat_reply("sys", [], "hello")

    @patch('ai_services.gemini.requests.post')
    def test_api_timeout_handling(self, mock_post):
        mock_post.side_effect = requests.exceptions.Timeout("Read timed out")
        client = GeminiClient(api_key='valid-test-key', timeout=5)
        with self.assertRaises(APITimeoutError):
            client.generate_chat_reply("sys", [], "hello")

    def test_secret_scrubbing(self):
        fake_key = "AQ.DummyTestKeyFormat000000000000000000"
        leaked = f"Error using key {fake_key} and AIzaSyDummySecretKeyValue123456789"
        cleaned = _scrub_secret(leaked, fake_key)
        self.assertNotIn(fake_key, cleaned)
        self.assertNotIn("AIzaSy", cleaned)


class NexusChatbotViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        Profile.load()
        self.ai_cfg = AISettings.load()
        self.ai_cfg.chat_enabled = True
        self.ai_cfg.chat_daily_limit_per_visitor = 5
        self.ai_cfg.chat_rate_limit_per_minute = 4
        self.ai_cfg.save()
        self.chat_url = reverse('nexus:chat')

    def test_system_prompt_excludes_private_data(self):
        """Ensure visitor contact messages are NEVER leaked into AI system instructions."""
        ContactMessage.objects.create(
            name="Confidential Sender",
            email="secret@private.org",
            subject="Private Contract",
            message="SECRET_PAYLOAD_DO_NOT_EXPOSE",
        )
        prompt = build_nexus_system_prompt()
        self.assertIn("Abhiram Anil", prompt)
        self.assertNotIn("SECRET_PAYLOAD_DO_NOT_EXPOSE", prompt)
        self.assertNotIn("secret@private.org", prompt)

    def test_missing_api_key_returns_friendly_503(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': ''}, clear=False):
            res = self.client.post(
                self.chat_url,
                data=json.dumps({'message': 'Explain VLANs'}),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 503)
            self.assertEqual(res.json()['code'], 'missing_api_key')

    def test_empty_message_rejected(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-present'}, clear=False):
            res = self.client.post(
                self.chat_url,
                data=json.dumps({'message': '   '}),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()['code'], 'empty_message')

    def test_long_message_rejected(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-present'}, clear=False):
            res = self.client.post(
                self.chat_url,
                data=json.dumps({'message': 'A' * 1600}),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()['code'], 'message_too_long')

    @patch('ai_services.gemini.requests.post')
    def test_conversation_history_capping_and_valid_reply(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'A VLAN partitions broadcast domains at Layer 2.'}]}}],
            'usageMetadata': {'promptTokenCount': 20, 'candidatesTokenCount': 12, 'totalTokenCount': 32},
        }
        mock_post.return_value = resp

        oversized_history = [{'role': 'user' if i % 2 == 0 else 'model', 'content': f'turn {i}'} for i in range(25)]

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-present'}, clear=False):
            res = self.client.post(
                self.chat_url,
                data=json.dumps({'message': 'What is a VLAN?', 'history': oversized_history}),
                content_type='application/json'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data['status'], 'ok')
            self.assertIn('VLAN', data['reply'])

            # Verify sent history to Gemini was capped to MAX_HISTORY_ITEMS (10) + 1 current msg = 11
            sent_payload = mock_post.call_args.kwargs['json']
            self.assertLessEqual(len(sent_payload['contents']), 11)
            # Verify no message content stored in DB logs
            self.assertEqual(ChatUsageLog.objects.count(), 1)

    @patch('ai_services.gemini.requests.post')
    def test_rate_limiting_and_daily_quota_enforcement(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': 'OK'}]}}],
            'usageMetadata': {'totalTokenCount': 5},
        }
        mock_post.return_value = resp

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key-present'}, clear=False):
            for i in range(4):
                r = self.client.post(
                    self.chat_url,
                    data=json.dumps({'message': f'Question {i}'}),
                    content_type='application/json'
                )
                self.assertEqual(r.status_code, 200)

            # 5th request in <60s hits per-minute burst limit (4/min)
            blocked = self.client.post(
                self.chat_url,
                data=json.dumps({'message': 'Burst message'}),
                content_type='application/json'
            )
            self.assertEqual(blocked.status_code, 429)
            self.assertEqual(blocked.json()['code'], 'rate_limited')

    def test_api_key_never_rendered_in_homepage_html(self):
        secret = "AQ.DummyTestSecretShouldNeverAppearInHtml999"
        with patch.dict(os.environ, {'GEMINI_API_KEY': secret}, clear=False):
            res = self.client.get(reverse('home'))
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(secret.encode('utf-8'), res.content)
            self.assertContains(res, "NEXUS AI")
            self.assertContains(res, "NETWORK INTELLIGENCE")
