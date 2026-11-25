"""
Centralized Google Gemini REST API Service (v1beta).
Designed for zero heavy dependencies and full compatibility with PythonAnywhere Free Tier.
Never exposes GEMINI_API_KEY in URLs, exceptions, logs, or templates.
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from core.security import log_security_event

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Base exception for Gemini API errors with user-safe messages."""
    code = 'gemini_error'
    user_message = "AI service is temporarily unavailable. Please try again later."

    def __init__(self, message: str = '', user_message: str = ''):
        super().__init__(message or self.user_message)
        if user_message:
            self.user_message = user_message


class MissingAPIKeyError(GeminiServiceError):
    code = 'missing_api_key'
    user_message = "AI features are currently offline (API credentials not configured on server)."


class InvalidAPIKeyError(GeminiServiceError):
    code = 'invalid_api_key'
    user_message = "AI authentication failed. Please contact the site administrator."


class QuotaExceededError(GeminiServiceError):
    code = 'quota_exceeded'
    user_message = "Gemini API free-tier quota has been reached temporarily. Please try again later."


class APITimeoutError(GeminiServiceError):
    code = 'api_timeout'
    user_message = "The AI engine took too long to respond. Please try a shorter query or retry shortly."


class ConnectivityBlockedError(GeminiServiceError):
    code = 'connectivity_blocked'
    user_message = "Outbound connection to Gemini API could not be completed from this server environment."


class ModelUnavailableError(GeminiServiceError):
    code = 'model_unavailable'
    user_message = "The configured Gemini model is temporarily overloaded or unavailable."


class InvalidAIResponseError(GeminiServiceError):
    code = 'invalid_response'
    user_message = "Received an incomplete or malformed response from the AI engine. Please try again."


@dataclass
class GeminiResponse:
    text: str
    model: str
    token_usage: Dict[str, int]


DEFAULT_FLASH_MODEL = 'gemini-3.5-flash-lite'
FALLBACK_FLASH_MODELS = [
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3-flash-preview',
    'gemini-3.8-flash',
]


def get_gemini_config() -> Dict[str, Any]:
    """Read Gemini configuration dynamically from environment and non-secret AISettings."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    env_model = os.environ.get('GEMINI_MODEL', DEFAULT_FLASH_MODEL).strip() or DEFAULT_FLASH_MODEL
    timeout = int(os.environ.get('GEMINI_API_TIMEOUT', '25') or 25)
    chat_enabled = os.environ.get('GEMINI_CHAT_ENABLED', 'True').strip().lower() in ('true', '1', 'yes')
    article_enabled = os.environ.get('GEMINI_DAILY_ARTICLE_ENABLED', 'True').strip().lower() in ('true', '1', 'yes')
    publish_mode = os.environ.get('GEMINI_ARTICLE_PUBLISH_MODE', 'review').strip().lower()
    if publish_mode not in ('auto', 'review', 'manual'):
        publish_mode = 'review'

    try:
        daily_limit = max(1, int(os.environ.get('GEMINI_DAILY_REQUEST_LIMIT', '10') or 10))
    except ValueError:
        daily_limit = 10

    # Merge non-secret runtime overrides from AISettings if DB is ready
    preferred_model = env_model
    rate_per_minute = 6
    timezone_name = 'Asia/Kolkata'
    try:
        from intelligence.models import AISettings
        ai_cfg = AISettings.load()
        chat_enabled = chat_enabled and ai_cfg.chat_enabled
        article_enabled = article_enabled and ai_cfg.daily_article_enabled
        if ai_cfg.article_publish_mode in ('auto', 'review', 'manual'):
            publish_mode = ai_cfg.article_publish_mode
        if ai_cfg.preferred_model:
            preferred_model = ai_cfg.preferred_model.strip()
        daily_limit = ai_cfg.chat_daily_limit_per_visitor or daily_limit
        rate_per_minute = ai_cfg.chat_rate_limit_per_minute or rate_per_minute
        timezone_name = ai_cfg.article_generation_timezone or timezone_name
    except Exception:
        pass

    return {
        'api_key_configured': bool(api_key),
        'model': preferred_model,
        'timeout': max(5, min(timeout, 60)),
        'chat_enabled': chat_enabled,
        'daily_article_enabled': article_enabled,
        'publish_mode': publish_mode,
        'daily_limit': daily_limit,
        'rate_per_minute': rate_per_minute,
        'timezone': timezone_name,
    }


def _scrub_secret(text: str, secret: str) -> str:
    """Ensure secret API key can never leak into outputs or error logs."""
    if not text:
        return ''
    if secret:
        text = text.replace(secret, '[REDACTED_API_KEY]')
    # Defensive mask for common Google key formats just in case
    text = re.sub(r'(AIza[0-9A-Za-z\-_]{20,}|AQ\.[0-9A-Za-z\-_]{20,})', '[REDACTED_KEY]', text)
    return text


class GeminiClient:
    """Stateless synchronous client for Google Gemini v1beta REST API."""

    BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/models'

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, timeout: Optional[int] = None):
        cfg = get_gemini_config()
        self.api_key = (api_key if api_key is not None else os.environ.get('GEMINI_API_KEY', '')).strip()
        self.model = (model or cfg['model']).strip()
        self.timeout = timeout or cfg['timeout']

    def _build_candidate_models(self) -> List[str]:
        candidates = [self.model]
        for fb in FALLBACK_FLASH_MODELS:
            if fb not in candidates:
                candidates.append(fb)
        return candidates

    def _post_generate_content(self, payload: Dict[str, Any], allow_fallback: bool = True) -> GeminiResponse:
        if not self.api_key:
            raise MissingAPIKeyError()

        models_to_try = self._build_candidate_models() if allow_fallback else [self.model]
        last_error: Optional[GeminiServiceError] = None

        for model_name in models_to_try:
            # Strict SSRF / URL-path-injection validation on model name
            if not re.fullmatch(r'[a-zA-Z0-9._\-]{3,64}', model_name):
                log_security_event('GEMINI_INVALID_MODEL', f"Rejected invalid model name pattern: {model_name}")
                raise ModelUnavailableError("Invalid Gemini model identifier configured.")

            url = f"{self.BASE_URL}/{model_name}:generateContent"
            headers = {
                'x-goog-api-key': self.api_key,
                'Content-Type': 'application/json',
            }

            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            except requests.exceptions.Timeout as exc:
                log_security_event('GEMINI_TIMEOUT', f"Model {model_name} timed out after {self.timeout}s")
                last_error = APITimeoutError(f"Request timed out after {self.timeout}s")
                continue
            except requests.exceptions.ProxyError as exc:
                log_security_event('GEMINI_PROXY_BLOCKED', f"Proxy blocked Gemini request: {type(exc).__name__}")
                raise ConnectivityBlockedError(f"Outbound proxy restricted Gemini endpoint: {type(exc).__name__}")
            except requests.exceptions.ConnectionError as exc:
                log_security_event('GEMINI_CONNECTION_ERROR', f"Network error reaching Gemini: {type(exc).__name__}")
                raise ConnectivityBlockedError(f"Network connection to Gemini failed: {type(exc).__name__}")
            except requests.exceptions.RequestException as exc:
                raise GeminiServiceError(f"HTTP error: {type(exc).__name__}")

            if resp.status_code == 200:
                return self._parse_success_response(resp.json(), model_name)

            # Classify HTTP error safely without exposing secrets
            err_msg = ''
            try:
                err_msg = resp.json().get('error', {}).get('message', '')
            except Exception:
                err_msg = resp.text[:250]
            err_msg = _scrub_secret(err_msg, self.api_key)

            if resp.status_code in (400, 401, 403):
                log_security_event('GEMINI_AUTH_ERROR', f"Status {resp.status_code} for {model_name}: {err_msg}")
                lower = err_msg.lower()
                if 'api key' in lower or 'key not valid' in lower or resp.status_code == 401:
                    raise InvalidAPIKeyError(f"Auth failure ({resp.status_code}): {err_msg}")
                if resp.status_code == 403:
                    raise InvalidAPIKeyError(f"Permission denied ({resp.status_code}): {err_msg}")
                raise GeminiServiceError(f"Bad request ({resp.status_code}): {err_msg}")

            if resp.status_code == 429:
                log_security_event('GEMINI_QUOTA_EXCEEDED', f"HTTP 429 for {model_name}: {err_msg}")
                raise QuotaExceededError(f"Rate/Quota limit exceeded: {err_msg}")

            if resp.status_code in (404, 500, 502, 503, 504):
                last_error = ModelUnavailableError(
                    f"Model {model_name} returned {resp.status_code}: {err_msg}"
                )
                logger.warning("Gemini fallback triggered from %s (%s)", model_name, resp.status_code)
                continue

            raise GeminiServiceError(f"Unexpected Gemini status {resp.status_code}: {err_msg}")

        if last_error:
            raise last_error
        raise ModelUnavailableError("No Flash models responded successfully.")

    def _parse_success_response(self, data: Dict[str, Any], model_name: str) -> GeminiResponse:
        candidates = data.get('candidates') or []
        if not candidates:
            prompt_feedback = data.get('promptFeedback', {})
            block_reason = prompt_feedback.get('blockReason', '')
            if block_reason:
                raise InvalidAIResponseError(
                    f"Blocked by safety filter: {block_reason}",
                    user_message="That request triggered safety guidelines and cannot be answered."
                )
            raise InvalidAIResponseError("Empty candidates list returned by Gemini.")

        first = candidates[0]
        finish_reason = first.get('finishReason', '')
        if finish_reason == 'SAFETY':
            raise InvalidAIResponseError(
                "Response stopped by safety filters",
                user_message="I cannot provide an answer that violates security/safety guidelines."
            )

        parts = first.get('content', {}).get('parts') or []
        text_chunks = [p.get('text', '') for p in parts if isinstance(p, dict) and p.get('text')]
        text = '\n'.join(text_chunks).strip()
        if not text:
            raise InvalidAIResponseError("Empty text content in Gemini candidate.")

        text = _scrub_secret(text, self.api_key)

        usage_raw = data.get('usageMetadata') or {}
        usage = {
            'prompt_tokens': int(usage_raw.get('promptTokenCount', 0) or 0),
            'candidates_tokens': int(usage_raw.get('candidatesTokenCount', 0) or 0),
            'total_tokens': int(usage_raw.get('totalTokenCount', 0) or 0),
        }
        return GeminiResponse(text=text, model=model_name, token_usage=usage)

    def generate_chat_reply(
        self,
        system_instruction: str,
        history: List[Dict[str, str]],
        user_message: str,
        max_output_tokens: int = 1024,
        temperature: float = 0.4,
    ) -> GeminiResponse:
        """Send multi-turn conversation to Gemini with system instruction."""
        contents = []
        for turn in history:
            role = 'model' if turn.get('role') == 'model' else 'user'
            content = str(turn.get('content', '')).strip()
            if content:
                contents.append({'role': role, 'parts': [{'text': content}]})

        contents.append({'role': 'user', 'parts': [{'text': user_message.strip()}]})

        payload = {
            'systemInstruction': {
                'parts': [{'text': system_instruction}]
            },
            'contents': contents,
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_output_tokens,
            }
        }
        return self._post_generate_content(payload, allow_fallback=True)

    def generate_structured_json(
        self,
        system_instruction: str,
        prompt: str,
        max_output_tokens: int = 4096,
        temperature: float = 0.35,
    ) -> Dict[str, Any]:
        """Request strict JSON output and return parsed payload + metadata."""
        payload = {
            'systemInstruction': {
                'parts': [{'text': system_instruction}]
            },
            'contents': [
                {'role': 'user', 'parts': [{'text': prompt}]}
            ],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_output_tokens,
                'responseMimeType': 'application/json',
            }
        }
        resp = self._post_generate_content(payload, allow_fallback=True)
        raw_text = resp.text.strip()

        # Strip optional markdown code fences if a model still wraps JSON
        if raw_text.startswith('```'):
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text, flags=re.IGNORECASE)
            raw_text = re.sub(r'\s*```$', '', raw_text)

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise InvalidAIResponseError(f"Invalid JSON from Gemini: {exc}")

        if not isinstance(parsed, dict):
            raise InvalidAIResponseError("Expected top-level JSON object from Gemini.")

        return {
            'data': parsed,
            'model': resp.model,
            'token_usage': resp.token_usage,
        }
