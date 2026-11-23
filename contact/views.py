from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import ContactMessage
from .forms import ContactForm


def get_client_ip(request):
    """Safely extracts client IP address accounting for proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def contact_submit_view(request):
    if request.method != 'POST':
        return redirect('home')

    # Rate limiting: maximum 5 messages per IP in the last 15 minutes
    client_ip = get_client_ip(request)
    recent_threshold = timezone.now() - timedelta(minutes=15)
    
    recent_count = ContactMessage.objects.filter(
        ip_address=client_ip,
        created_at__gte=recent_threshold
    ).count()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.POST.get('is_ajax') == '1'
    )

    if recent_count >= 5:
        err_msg = "Rate limit exceeded. Transmission blocked to prevent buffer overflow. Please try again in 15 minutes."
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': err_msg}, status=429)
        messages.error(request, err_msg)
        return redirect('/#contact')

    form = ContactForm(request.POST)
    if form.is_valid():
        contact_msg = form.save(commit=False)
        contact_msg.ip_address = client_ip
        contact_msg.save()

        success_msg = f"Transmission received successfully. Thank you, {contact_msg.name}! Your payload has been queued for review."
        if is_ajax:
            return JsonResponse({'status': 'success', 'message': success_msg})
        messages.success(request, success_msg)
        return redirect('/#contact')
    else:
        # Collect first error
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(f"{field.capitalize()}: {error}")
        err_msg = "Transmission validation failed: " + "; ".join(error_list)

        if is_ajax:
            return JsonResponse({'status': 'error', 'message': err_msg, 'errors': form.errors}, status=400)
        messages.error(request, err_msg)
        return redirect('/#contact')
