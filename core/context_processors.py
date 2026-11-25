from django.utils import timezone
from .models import PortfolioSettings
from portfolio.models import Profile, SocialLink


def global_portfolio_context(request):
    """
    Supplies portfolio metadata and settings to all templates safely,
    with defensive exception handling if migrations haven't run yet.
    """
    try:
        settings_obj = PortfolioSettings.load()
    except Exception:
        settings_obj = None

    try:
        profile_obj = Profile.load()
    except Exception:
        profile_obj = None

    try:
        social_links = list(SocialLink.objects.filter(is_active=True))
    except Exception:
        social_links = []

    ai_public_status = {'chat_enabled': True, 'api_key_configured': False, 'daily_article_enabled': True, 'daily_limit': 10}
    try:
        from ai_services.gemini import get_gemini_config
        cfg = get_gemini_config()
        # Strictly non-secret metadata only — NEVER expose API keys
        ai_public_status = {
            'chat_enabled': cfg['chat_enabled'],
            'api_key_configured': cfg['api_key_configured'],
            'daily_article_enabled': cfg['daily_article_enabled'],
            'daily_limit': cfg['daily_limit'],
        }
    except Exception:
        pass

    return {
        'site_settings': settings_obj,
        'profile': profile_obj,
        'social_links': social_links,
        'ai_status': ai_public_status,
        'current_year': timezone.now().year,
    }
