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

    return {
        'site_settings': settings_obj,
        'profile': profile_obj,
        'social_links': social_links,
        'current_year': timezone.now().year,
    }
