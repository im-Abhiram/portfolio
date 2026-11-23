from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory, SecurityNote


def journal_list_view(request):
    category_slug = request.GET.get('category')
    categories = BlogCategory.objects.all()
    posts = BlogPost.objects.filter(is_published=True)
    security_notes = SecurityNote.objects.filter(is_published=True)

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    return render(request, 'journal/journal_list.html', {
        'posts': posts,
        'categories': categories,
        'security_notes': security_notes,
        'active_category': category_slug,
    })


def journal_detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:3]

    return render(request, 'journal/journal_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })
