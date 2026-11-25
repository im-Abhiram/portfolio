from datetime import timedelta

from django.contrib import messages
from django.contrib.syndication.views import Feed
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from contact.views import get_client_ip
from .models import DailyArticle, IntelSubscriber


def intelligence_list_view(request):
    """
    Public NETWORK INTELLIGENCE archive with search, 7-category filters,
    featured today's article, pagination, and local watchlist signup.
    """
    category = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()

    all_published = DailyArticle.objects.filter(status='published')
    categories = [c[0] for c in DailyArticle.CATEGORY_CHOICES]

    # Featured article (when browsing default unfiltered page 1)
    featured_article = None
    if not category and not search_query and request.GET.get('page', '1') == '1':
        featured_article = all_published.filter(is_featured=True).first() or all_published.first()

    articles_qs = all_published
    if category and category in categories:
        articles_qs = articles_qs.filter(category=category)
    else:
        category = ''

    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query) |
            Q(subtitle__icontains=search_query) |
            Q(introduction__icontains=search_query) |
            Q(tags__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    if featured_article:
        articles_qs = articles_qs.exclude(pk=featured_article.pk)

    paginator = Paginator(articles_qs, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'intelligence/list.html', {
        'featured_article': featured_article,
        'page_obj': page_obj,
        'articles': page_obj.object_list,
        'categories': categories,
        'active_category': category,
        'search_query': search_query,
        'total_published': all_published.count(),
    })


def intelligence_detail_view(request, slug):
    """
    Editorial reader view for NETWORK INTELLIGENCE articles.
    Supports staff preview for draft/pending_review articles.
    """
    preview_requested = request.GET.get('preview') == '1'
    if preview_requested and request.user.is_authenticated and request.user.is_staff:
        article = get_object_or_404(DailyArticle, slug=slug)
        is_preview = article.status != 'published'
    else:
        article = get_object_or_404(DailyArticle, slug=slug, status='published')
        is_preview = False

    published_qs = DailyArticle.objects.filter(status='published')
    related_articles = published_qs.filter(category=article.category).exclude(pk=article.pk)[:3]

    # Previous (older) and Next (newer) article navigation
    prev_article = None
    next_article = None
    if article.published_at:
        prev_article = published_qs.filter(
            Q(published_at__lt=article.published_at) |
            Q(published_at=article.published_at, pk__lt=article.pk)
        ).exclude(pk=article.pk).order_by('-published_at', '-pk').first()

        next_article = published_qs.filter(
            Q(published_at__gt=article.published_at) |
            Q(published_at=article.published_at, pk__gt=article.pk)
        ).exclude(pk=article.pk).order_by('published_at', 'pk').first()

    return render(request, 'intelligence/detail.html', {
        'article': article,
        'content': article.content or {},
        'related_articles': related_articles,
        'prev_article': prev_article,
        'next_article': next_article,
        'is_preview': is_preview,
    })


@require_POST
def digest_subscribe_view(request):
    """
    Honest local-only watchlist registration.
    Explicitly communicates that emails are stored locally without claiming outbound SMTP delivery.
    """
    raw_email = (request.POST.get('email') or '').strip().lower()
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    try:
        validate_email(raw_email)
    except ValidationError:
        msg = "Please enter a valid email address."
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect('intelligence:list')

    client_ip = get_client_ip(request)
    recent_threshold = timezone.now() - timedelta(minutes=15)
    if IntelSubscriber.objects.filter(ip_address=client_ip, created_at__gte=recent_threshold).count() >= 5:
        msg = "Too many subscription requests from this address. Please try again later."
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=429)
        messages.error(request, msg)
        return redirect('intelligence:list')

    sub, created = IntelSubscriber.objects.get_or_create(
        email=raw_email,
        defaults={'ip_address': client_ip}
    )
    if created:
        msg = "Registered on the local digest watchlist (stored in database; use our RSS feed for live automated updates)."
    else:
        msg = "Your address is already registered on the local digest watchlist."

    if is_ajax:
        return JsonResponse({'status': 'ok', 'message': msg})
    messages.success(request, msg)
    return redirect('intelligence:list')


class IntelligenceRssFeed(Feed):
    title = "NETWORK INTELLIGENCE — Daily Networking & Cybersecurity Concepts"
    link = "/intelligence/"
    description = "One day. One concept. Better technical knowledge."

    def items(self):
        return DailyArticle.objects.filter(status='published')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return f"{item.subtitle} — {item.introduction[:260]}"

    def item_link(self, item):
        return reverse('intelligence:detail', args=[item.slug])
