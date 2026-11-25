import hashlib
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from ai_services.gemini import (
    GeminiClient,
    GeminiServiceError,
    get_gemini_config,
)
from core.security import get_client_ip, log_security_event

from .models import ChatUsageLog
from .prompts import build_nexus_system_prompt

logger = logging.getLogger(__name__)

MAX_REQUEST_BODY_BYTES = 32 * 1024  # 32 KB hard limit
MAX_MESSAGE_LENGTH = 1500
MAX_HISTORY_ITEMS = 10  # Max 5 user+model exchanges sent to Gemini
MAX_HISTORY_ENTRY_LENGTH = 2500
DAILY_GLOBAL_BUDGET = 250


def _get_session_hash(request) -> str:
    if not request.session.session_key:
        request.session.create()
    raw_key = request.session.session_key or 'anon'
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()[:16]


def _check_usage_limits(request, client_ip: str, session_hash: str, cfg: dict):
    """Returns (allowed: bool, remaining_today: int, error_message: str)."""
    now = timezone.now()
    today = timezone.localdate()

    # 1. Global daily safety budget (protect free tier account)
    global_count = ChatUsageLog.objects.filter(usage_date=today, status='ok').count()
    if global_count >= DAILY_GLOBAL_BUDGET:
        return False, 0, "ramo.ai has reached today's global free-tier service capacity. Please check back tomorrow."

    # 2. Short-window burst limit (per-minute per IP)
    one_min_ago = now - timedelta(seconds=60)
    recent_burst = ChatUsageLog.objects.filter(
        ip_address=client_ip,
        created_at__gte=one_min_ago,
    ).count()
    rate_per_min = int(cfg.get('rate_per_minute', 6))
    if recent_burst >= rate_per_min:
        return False, 0, "Rate limit exceeded: please wait a minute before sending more messages."

    # 3. Per-visitor daily limit (IP or session)
    daily_limit = int(cfg.get('daily_limit', 10))
    from django.db.models import Q
    visitor_today = ChatUsageLog.objects.filter(
        Q(ip_address=client_ip) | Q(session_hash=session_hash),
        usage_date=today,
        status='ok'
    ).count()

    remaining = max(0, daily_limit - visitor_today)
    if visitor_today >= daily_limit:
        return False, 0, (
            f"You have reached your daily limit of {daily_limit} ramo.ai questions on this free-tier portfolio. "
            "Please return tomorrow or reach out via the Contact section."
        )

    return True, remaining, ''


@require_GET
def nexus_status_api(request):
    """Returns safe public configuration status for NEXUS AI without exposing any credentials."""
    cfg = get_gemini_config()
    client_ip = get_client_ip(request)
    session_hash = _get_session_hash(request)
    allowed, remaining, _ = _check_usage_limits(request, client_ip, session_hash, cfg)

    available = bool(cfg['chat_enabled'] and cfg['api_key_configured'])
    notice = ''
    if not cfg['chat_enabled']:
        notice = "ramo.ai assistant is currently disabled by the administrator."
    elif not cfg['api_key_configured']:
        notice = "ramo.ai is currently offline (API key not configured on server)."

    return JsonResponse({
        'status': 'ok',
        'available': available,
        'enabled': cfg['chat_enabled'],
        'configured': cfg['api_key_configured'],
        'daily_limit': cfg['daily_limit'],
        'remaining_today': remaining if available else 0,
        'rate_allowed': allowed,
        'notice': notice,
    })


@require_POST
def nexus_chat_api(request):
    """
    CSRF-protected public API endpoint for NEXUS AI Chatbot.
    Never exposes credentials and never stores conversation content.
    """
    cfg = get_gemini_config()

    if not cfg['chat_enabled']:
        return JsonResponse({
            'status': 'error',
            'code': 'chat_disabled',
            'message': "ramo.ai is currently paused by the administrator."
        }, status=503)

    if not cfg['api_key_configured']:
        return JsonResponse({
            'status': 'error',
            'code': 'missing_api_key',
            'message': "ramo.ai is currently unavailable because Gemini API credentials are not configured on the server."
        }, status=503)

    # 1. Request payload size check
    if request.body and len(request.body) > MAX_REQUEST_BODY_BYTES:
        return JsonResponse({
            'status': 'error',
            'code': 'payload_too_large',
            'message': "Request payload exceeds maximum allowed size."
        }, status=400)

    # 2. Parse JSON safely
    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({
            'status': 'error',
            'code': 'invalid_json',
            'message': "Invalid JSON request format."
        }, status=400)

    if not isinstance(data, dict):
        return JsonResponse({
            'status': 'error',
            'code': 'invalid_payload',
            'message': "Payload must be a JSON object."
        }, status=400)

    # 3. Validate user message
    raw_message = data.get('message', '')
    if not isinstance(raw_message, str):
        return JsonResponse({
            'status': 'error',
            'code': 'invalid_message_type',
            'message': "Message must be plain text."
        }, status=400)

    user_message = raw_message.strip()
    if not user_message:
        return JsonResponse({
            'status': 'error',
            'code': 'empty_message',
            'message': "Please enter a question before sending."
        }, status=400)

    if len(user_message) > MAX_MESSAGE_LENGTH:
        return JsonResponse({
            'status': 'error',
            'code': 'message_too_long',
            'message': f"Message exceeds maximum allowed length of {MAX_MESSAGE_LENGTH} characters."
        }, status=400)

    # 4. Validate and cap conversation history
    raw_history = data.get('history', [])
    clean_history = []
    if isinstance(raw_history, list):
        # Slice to recent turns only to control token consumption
        for entry in raw_history[-MAX_HISTORY_ITEMS:]:
            if not isinstance(entry, dict):
                continue
            role = entry.get('role')
            content = entry.get('content', '')
            if role in ('user', 'model') and isinstance(content, str):
                trimmed = content.strip()[:MAX_HISTORY_ENTRY_LENGTH]
                if trimmed:
                    clean_history.append({'role': role, 'content': trimmed})

    # 5. Enforce per-IP & per-session rate & daily quota limits
    client_ip = get_client_ip(request)
    session_hash = _get_session_hash(request)
    allowed, remaining, limit_msg = _check_usage_limits(request, client_ip, session_hash, cfg)
    if not allowed:
        log_security_event('AI_CHAT_RATE_LIMIT', limit_msg, request=request)
        return JsonResponse({
            'status': 'error',
            'code': 'rate_limited',
            'message': limit_msg,
            'remaining_today': 0,
        }, status=429)

    # 6. Execute Gemini API call synchronously on server
    try:
        system_instruction = build_nexus_system_prompt()
        client = GeminiClient()
        ai_resp = client.generate_chat_reply(
            system_instruction=system_instruction,
            history=clean_history,
            user_message=user_message,
            max_output_tokens=1100,
            temperature=0.4,
        )

        # Log anonymized usage metric (NEVER logging user_message or ai_resp.text)
        ChatUsageLog.objects.create(
            ip_address=client_ip,
            session_hash=session_hash,
            usage_date=timezone.localdate(),
            status='ok',
            model_used=ai_resp.model,
            total_tokens=ai_resp.token_usage.get('total_tokens', 0),
        )

        return JsonResponse({
            'status': 'ok',
            'reply': ai_resp.text,
            'remaining_today': max(0, remaining - 1),
        })

    except GeminiServiceError as exc:
        logger.warning("NEXUS AI service error (%s): %s", exc.code, str(exc))
        ChatUsageLog.objects.create(
            ip_address=client_ip,
            session_hash=session_hash,
            usage_date=timezone.localdate(),
            status=exc.code[:30],
        )
        http_status = 429 if exc.code == 'quota_exceeded' else 503
        return JsonResponse({
            'status': 'error',
            'code': exc.code,
            'message': exc.user_message,
        }, status=http_status)
    except Exception:
        logger.exception("Unexpected exception in NEXUS AI chat endpoint")
        return JsonResponse({
            'status': 'error',
            'code': 'internal_error',
            'message': "An unexpected issue occurred while processing your question. Please retry shortly."
        }, status=503)
