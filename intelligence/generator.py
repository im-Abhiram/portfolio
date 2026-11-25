"""
Daily Article Generation & Validation Pipeline for NETWORK INTELLIGENCE.
Ensures idempotent execution, strict JSON schema validation, duplicate prevention,
safe content storage (never trusting raw AI HTML), and graceful error logging.
"""

import difflib
import hashlib
import logging
import re
from datetime import date, datetime
from typing import Any, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.text import slugify

from ai_services.gemini import (
    GeminiClient,
    GeminiServiceError,
    InvalidAIResponseError,
    get_gemini_config,
)

from .models import AISettings, ArticleGenerationLog, DailyArticle
from .topics import TOPIC_BANK

logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = [c[0] for c in DailyArticle.CATEGORY_CHOICES]


class DuplicateArticleError(Exception):
    """Raised when generated or imported article duplicates an existing one."""


class ArticleValidationError(Exception):
    """Raised when structured article payload fails schema/safety checks."""


def get_local_date(tz_name: Optional[str] = None) -> date:
    """Resolve current calendar date in configured timezone (defaults to Asia/Kolkata)."""
    cfg = get_gemini_config()
    tz = tz_name or cfg.get('timezone') or 'Asia/Kolkata'
    try:
        zone = ZoneInfo(tz)
    except Exception:
        zone = ZoneInfo('Asia/Kolkata')
    return datetime.now(zone).date()


def _sanitize_prose(value: Any, max_len: int = 8000) -> str:
    """Strips HTML tags from prose fields so templates render safe plain text."""
    if not isinstance(value, str):
        value = str(value or '')
    cleaned = re.sub(r'<[^>]+>', '', value)
    return cleaned.strip()[:max_len]


def _sanitize_list_of_strings(value: Any, max_items: int = 10, max_item_len: int = 400) -> list:
    if not isinstance(value, list):
        if isinstance(value, str) and value.strip():
            value = [line.strip('- ').strip() for line in value.splitlines() if line.strip()]
        else:
            return []
    result = []
    for item in value[:max_items]:
        text = _sanitize_prose(item, max_len=max_item_len)
        if text:
            result.append(text)
    return result


def validate_article_payload(raw_data: Dict[str, Any], fallback_category: str = 'Networking') -> Dict[str, Any]:
    """
    Validates and normalizes the 16-part article structure returned by Gemini or JSON import.
    Raises ArticleValidationError if critical blocks are missing or invalid.
    """
    if not isinstance(raw_data, dict):
        raise ArticleValidationError("Article payload must be a JSON object.")

    title = _sanitize_prose(raw_data.get('title', ''), max_len=240)
    subtitle = _sanitize_prose(raw_data.get('subtitle', ''), max_len=300)
    introduction = _sanitize_prose(raw_data.get('introduction', ''), max_len=4000)
    what_is_it = _sanitize_prose(raw_data.get('what_is_it', ''), max_len=5000)
    how_it_works = _sanitize_prose(raw_data.get('how_it_works', ''), max_len=5000)
    technical_explanation = _sanitize_prose(raw_data.get('technical_explanation', ''), max_len=6000)
    practical_example = _sanitize_prose(raw_data.get('practical_example', ''), max_len=5000)
    security_implications = _sanitize_prose(raw_data.get('security_implications', ''), max_len=4000)

    required_text_fields = {
        'title': title,
        'subtitle': subtitle,
        'introduction': introduction,
        'what_is_it': what_is_it,
        'how_it_works': how_it_works,
        'technical_explanation': technical_explanation,
        'practical_example': practical_example,
        'security_implications': security_implications,
    }
    missing = [k for k, v in required_text_fields.items() if len(v) < 15]
    if missing:
        raise ArticleValidationError(f"Missing or incomplete required sections: {', '.join(missing)}")

    # Validate commands & configurations (safe plain text inside <pre><code>, never raw HTML execution)
    raw_cmds = raw_data.get('commands_and_configs', [])
    commands_and_configs = []
    if isinstance(raw_cmds, list):
        for item in raw_cmds[:8]:
            if isinstance(item, dict):
                cmd_text = str(item.get('command', '')).strip()[:2000]
                expl = _sanitize_prose(item.get('explanation', ''), max_len=1000)
                env_note = _sanitize_prose(item.get('environment_note', 'Lab / Educational Example'), max_len=120)
                if cmd_text or expl:
                    commands_and_configs.append({
                        'command': cmd_text,
                        'explanation': expl,
                        'environment_note': env_note or 'Lab / Educational Example',
                    })

    common_mistakes = _sanitize_list_of_strings(raw_data.get('common_mistakes', []), max_items=8)
    prevention_best_practices = _sanitize_list_of_strings(raw_data.get('prevention_best_practices', []), max_items=8)
    key_takeaways = _sanitize_list_of_strings(raw_data.get('key_takeaways', []), max_items=8)
    further_learning = _sanitize_list_of_strings(raw_data.get('further_learning', []), max_items=6)

    if not common_mistakes or not prevention_best_practices or not key_takeaways:
        raise ArticleValidationError(
            "Missing required bulleted lists (common_mistakes, prevention_best_practices, or key_takeaways)."
        )

    # Category normalization
    raw_cat = _sanitize_prose(raw_data.get('category', fallback_category), max_len=80)
    category = raw_cat if raw_cat in ALLOWED_CATEGORIES else fallback_category
    if category not in ALLOWED_CATEGORIES:
        category = 'Networking'

    # Tags
    raw_tags = raw_data.get('tags', [])
    if isinstance(raw_tags, list):
        tags_list = [_sanitize_prose(t, max_len=40) for t in raw_tags[:8] if _sanitize_prose(t, max_len=40)]
        tags = ', '.join(tags_list)
    else:
        tags = _sanitize_prose(raw_tags, max_len=280)

    # Reading time
    try:
        reading_time = int(raw_data.get('reading_time', 6) or 6)
        reading_time = max(2, min(reading_time, 25))
    except (TypeError, ValueError):
        reading_time = 6

    content_dict = {
        'what_is_it': what_is_it,
        'how_it_works': how_it_works,
        'technical_explanation': technical_explanation,
        'practical_example': practical_example,
        'commands_and_configs': commands_and_configs,
        'security_implications': security_implications,
        'common_mistakes': common_mistakes,
        'prevention_best_practices': prevention_best_practices,
        'key_takeaways': key_takeaways,
        'further_learning': further_learning,
    }

    return {
        'title': title,
        'subtitle': subtitle,
        'introduction': introduction,
        'content': content_dict,
        'category': category,
        'tags': tags,
        'reading_time': reading_time,
    }


def check_duplicate_article(title: str, introduction: str, content: dict) -> Optional[str]:
    """
    Returns an error reason string if an exact hash or near-duplicate title already exists.
    Returns None if unique.
    """
    body_part = str(content.get('what_is_it', '')) + str(content.get('technical_explanation', ''))
    normalized = ' '.join(f"{title} {introduction} {body_part}".lower().split())
    candidate_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    if DailyArticle.objects.filter(content_hash=candidate_hash).exists():
        return "Exact content hash already exists in database."

    norm_title = ' '.join(title.lower().split())
    for existing_title in DailyArticle.objects.values_list('title', flat=True)[:100]:
        ratio = difflib.SequenceMatcher(None, norm_title, ' '.join(existing_title.lower().split())).ratio()
        if ratio >= 0.85:
            return f"Near-duplicate title detected ({int(ratio * 100)}% similarity with '{existing_title}')."

    return None


def select_next_topic(explicit_topic: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Selects an unused topic from TOPIC_BANK.
    Returns (topic_key, topic_title, default_category).
    """
    if explicit_topic and explicit_topic.strip():
        clean_t = explicit_topic.strip()[:220]
        return slugify(clean_t)[:140], clean_t, 'Networking'

    used_keys = set(DailyArticle.objects.exclude(topic_key='').values_list('topic_key', flat=True))
    recent_logged_topics = set(
        ArticleGenerationLog.objects.filter(status='success').values_list('selected_topic', flat=True)[:30]
    )

    for item in TOPIC_BANK:
        if item['key'] not in used_keys and item['topic'] not in recent_logged_topics:
            return item['key'], item['topic'], item['category']

    # Fallback if entire topic bank has been covered: pick least-recently used
    for item in TOPIC_BANK:
        if item['topic'] not in recent_logged_topics:
            return f"{item['key']}-part2", f"{item['topic']} (Deep-Dive Architecture)", item['category']

    fallback = TOPIC_BANK[0]
    return f"{fallback['key']}-edition", f"{fallback['topic']} — Advanced Operational Guide", fallback['category']


def _build_unique_slug(title: str, target_date: Optional[date] = None) -> str:
    base = slugify(title)[:220] or 'network-intelligence-brief'
    if target_date:
        candidate = f"{base}-{target_date.strftime('%Y%m%d')}"
    else:
        candidate = base

    slug = candidate[:250]
    counter = 2
    while DailyArticle.objects.filter(slug=slug).exists():
        slug = f"{candidate[:235]}-{counter}"
        counter += 1
    return slug


def _build_article_prompts(topic: str, category: str) -> Tuple[str, str]:
    categories_str = ", ".join(ALLOWED_CATEGORIES)
    system_instruction = (
        "You are a Senior Network Infrastructure Engineer and Defensive Cybersecurity Educator writing for "
        "NETWORK INTELLIGENCE ('One day. One concept. Better technical knowledge.').\n"
        "STRICT EDITORIAL & SAFETY STANDARDS:\n"
        "1. Produce technically accurate, vendor-honest, educational engineering content.\n"
        "2. Clearly mark any sample commands or configurations as lab/educational examples and explain "
        "what every command does BEFORE presenting it.\n"
        "3. Use strictly defensive cybersecurity framing; NEVER encourage unauthorized scanning or testing.\n"
        "4. NEVER invent fake CVEs, fake exploit codes, fabricated breach statistics, or fabricated external URLs.\n"
        "5. Output ONLY valid raw JSON matching the requested schema (no markdown wrapping around the JSON object, "
        "no HTML tags inside prose values)."
    )

    prompt = f"""Write one thorough, beginner-accessible yet technically rigorous daily article on:
Topic: "{topic}"
Suggested Category (pick the best matching from [{categories_str}]): "{category}"

Return a single JSON object with EXACTLY these keys:
{{
  "title": "Compelling technical editorial title",
  "subtitle": "Concise 1-sentence subtitle summarizing the concept",
  "category": "One of: {categories_str}",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4"],
  "reading_time": 6,
  "introduction": "Engaging 2-paragraph introduction explaining why this concept matters in IT operations and cybersecurity.",
  "what_is_it": "Clear foundational explanation starting from first principles.",
  "how_it_works": "Step-by-step mechanical breakdown of packets, states, architecture, or code flow.",
  "technical_explanation": "Deeper architectural details, edge cases, protocols, ports, or implementation nuances.",
  "practical_example": "Concrete enterprise or authorized lab scenario showing how engineers encounter or configure this.",
  "commands_and_configs": [
    {{
      "explanation": "Clear explanation of what this diagnostic/configuration step achieves BEFORE running it.",
      "command": "Safe verified diagnostic command or illustrative config snippet (plain text)",
      "environment_note": "Lab / Illustrative Example"
    }}
  ],
  "security_implications": "Risks of misconfiguration, defensive considerations, and visibility/monitoring impact.",
  "common_mistakes": ["Mistake 1", "Mistake 2", "Mistake 3"],
  "prevention_best_practices": ["Best Practice 1", "Best Practice 2", "Best Practice 3", "Best Practice 4"],
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "further_learning": ["Next concept 1", "Next concept 2", "Official standard or topic to study next (no invented URLs)"]
}}"""
    return system_instruction, prompt


def _resolve_initial_status(publish_mode: str) -> str:
    if publish_mode == 'auto':
        return 'published'
    if publish_mode == 'manual':
        return 'draft'
    return 'pending_review'


def generate_daily_article(
    target_date: Optional[date] = None,
    explicit_topic: Optional[str] = None,
    publish_mode: Optional[str] = None,
    allow_regenerate_non_published: bool = False,
    dry_run: bool = False,
    client: Optional[GeminiClient] = None,
) -> Dict[str, Any]:
    """
    Executes the end-to-end daily article generation workflow safely & idempotently.
    Never overwrites an already-published article automatically.
    """
    cfg = get_gemini_config()
    date_obj = target_date or get_local_date(cfg.get('timezone'))
    mode = publish_mode or cfg.get('publish_mode', 'review')
    if mode not in ('auto', 'review', 'manual'):
        mode = 'review'

    # 1. Check if an article already exists for date_obj
    existing_for_date = DailyArticle.objects.filter(scheduled_date=date_obj).first()
    if existing_for_date:
        if existing_for_date.status == 'published' or not allow_regenerate_non_published:
            msg = f"Article already exists for {date_obj.isoformat()}: '{existing_for_date.title}' [{existing_for_date.status}]."
            if not dry_run:
                ArticleGenerationLog.objects.create(
                    generation_date=date_obj,
                    selected_topic=existing_for_date.title,
                    status='skipped',
                    error_message=msg,
                    generated_article=existing_for_date,
                )
            return {
                'status': 'skipped',
                'message': msg,
                'article': existing_for_date,
            }

    # 2. Pick topic
    topic_key, topic_title, default_category = select_next_topic(explicit_topic)

    if dry_run:
        return {
            'status': 'dry_run',
            'message': f"Dry run complete. Would generate topic '{topic_title}' ({default_category}) for {date_obj.isoformat()} in mode '{mode}'.",
            'topic': topic_title,
            'category': default_category,
            'target_date': date_obj.isoformat(),
        }

    # 3. Call Gemini API
    gemini_client = client or GeminiClient()
    sys_prompt, user_prompt = _build_article_prompts(topic_title, default_category)

    try:
        raw_result = gemini_client.generate_structured_json(
            system_instruction=sys_prompt,
            prompt=user_prompt,
            max_output_tokens=4096,
            temperature=0.35,
        )
        validated = validate_article_payload(raw_result['data'], fallback_category=default_category)
        model_used = raw_result.get('model', cfg.get('model', ''))
        token_usage = raw_result.get('token_usage', {})
    except (GeminiServiceError, ArticleValidationError) as exc:
        err_detail = str(exc)
        ArticleGenerationLog.objects.create(
            generation_date=date_obj,
            selected_topic=topic_title,
            status='failed',
            error_message=err_detail,
        )
        return {
            'status': 'failed',
            'message': getattr(exc, 'user_message', err_detail),
            'error': err_detail,
        }
    except Exception as exc:
        err_detail = f"Unexpected error: {type(exc).__name__}: {exc}"
        logger.exception("Unexpected failure generating daily article")
        ArticleGenerationLog.objects.create(
            generation_date=date_obj,
            selected_topic=topic_title,
            status='failed',
            error_message=err_detail,
        )
        return {
            'status': 'failed',
            'message': "Unexpected generation error occurred. Check generation logs.",
            'error': err_detail,
        }

    # 4. Duplicate check
    # If regenerating non-published for same date, exclude itself before duplicate check
    if existing_for_date and allow_regenerate_non_published:
        existing_for_date.delete()

    dup_reason = check_duplicate_article(
        validated['title'],
        validated['introduction'],
        validated['content'],
    )
    if dup_reason:
        ArticleGenerationLog.objects.create(
            generation_date=date_obj,
            selected_topic=topic_title,
            status='duplicate_blocked',
            error_message=dup_reason,
            model_used=model_used,
            token_usage=token_usage,
        )
        return {
            'status': 'duplicate_blocked',
            'message': dup_reason,
        }

    # 5. Persist atomically
    initial_status = _resolve_initial_status(mode)
    slug = _build_unique_slug(validated['title'], target_date=date_obj)

    try:
        with transaction.atomic():
            if initial_status == 'published':
                # Feature today's newly published article cleanly
                DailyArticle.objects.filter(is_featured=True).update(is_featured=False)

            article = DailyArticle.objects.create(
                title=validated['title'],
                slug=slug,
                subtitle=validated['subtitle'],
                introduction=validated['introduction'],
                content=validated['content'],
                category=validated['category'],
                tags=validated['tags'],
                reading_time=validated['reading_time'],
                scheduled_date=date_obj,
                topic_key=topic_key,
                status=initial_status,
                published_at=timezone.now() if initial_status == 'published' else None,
                is_featured=(initial_status == 'published'),
                ai_generated=True,
            )

            ArticleGenerationLog.objects.create(
                generation_date=date_obj,
                selected_topic=topic_title,
                status='success',
                generated_article=article,
                model_used=model_used,
                token_usage=token_usage,
            )

        return {
            'status': 'success',
            'message': f"Generated '{article.title}' ({article.get_status_display()}) for {date_obj.isoformat()}.",
            'article': article,
            'model_used': model_used,
            'token_usage': token_usage,
        }

    except IntegrityError as exc:
        msg = f"Database constraint prevented duplicate article for {date_obj.isoformat()}: {exc}"
        ArticleGenerationLog.objects.create(
            generation_date=date_obj,
            selected_topic=topic_title,
            status='duplicate_blocked',
            error_message=msg,
        )
        return {
            'status': 'duplicate_blocked',
            'message': msg,
        }


def import_article_from_json_payload(
    raw_data: Dict[str, Any],
    scheduled_date: Optional[date] = None,
    status: str = 'pending_review',
) -> DailyArticle:
    """
    Allows administrators to import validated structured JSON generated locally
    (e.g. if outbound access on PythonAnywhere free tier is restricted).
    """
    validated = validate_article_payload(raw_data)
    dup_reason = check_duplicate_article(
        validated['title'],
        validated['introduction'],
        validated['content'],
    )
    if dup_reason:
        raise DuplicateArticleError(dup_reason)

    if scheduled_date and DailyArticle.objects.filter(scheduled_date=scheduled_date).exists():
        raise DuplicateArticleError(f"An article for {scheduled_date.isoformat()} already exists.")

    if status not in ('draft', 'pending_review', 'published', 'archived'):
        status = 'pending_review'

    slug = _build_unique_slug(validated['title'], target_date=scheduled_date)
    with transaction.atomic():
        if status == 'published':
            DailyArticle.objects.filter(is_featured=True).update(is_featured=False)

        article = DailyArticle.objects.create(
            title=validated['title'],
            slug=slug,
            subtitle=validated['subtitle'],
            introduction=validated['introduction'],
            content=validated['content'],
            category=validated['category'],
            tags=validated['tags'],
            reading_time=validated['reading_time'],
            scheduled_date=scheduled_date,
            topic_key=slugify(validated['title'])[:140],
            status=status,
            published_at=timezone.now() if status == 'published' else None,
            is_featured=(status == 'published'),
            ai_generated=bool(raw_data.get('ai_generated', True)),
        )
    return article
