from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from core.security import get_client_ip, log_security_event
from .models import ContactMessage
from .forms import ContactForm

import time


def contact_submit_view(request):
    if request.method != 'POST':
        return redirect('home')

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        'application/json' in request.headers.get('Accept', '') or
        request.POST.get('is_ajax') == '1'
    )

    # 1. Rapid Flood / Bot Timing Protection (Session based)
    now_ts = time.time()
    last_submit = request.session.get('last_contact_ts', 0)
    if now_ts - last_submit < 3.0:
        err_msg = "Rapid automated submissions detected. Please wait a few seconds before retrying."
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': err_msg}, status=429)
        messages.error(request, err_msg)
        return redirect('/#contact')

    # 2. Rate limiting: maximum 5 messages per IP in the last 15 minutes
    client_ip = get_client_ip(request)
    recent_threshold = timezone.now() - timedelta(minutes=15)
    
    recent_count = ContactMessage.objects.filter(
        ip_address=client_ip,
        created_at__gte=recent_threshold
    ).count()

    if recent_count >= 5:
        log_security_event('CONTACT_RATE_LIMIT', 'Contact submission IP threshold exceeded (5/15min)', request=request)
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

        # Update session timestamp
        request.session['last_contact_ts'] = now_ts

        success_msg = f"Transmission received successfully. Thank you, {contact_msg.name}! Your payload has been queued for review."
        if is_ajax:
            return JsonResponse({'status': 'success', 'message': success_msg})
        messages.success(request, success_msg)
        return redirect('/#contact')
    else:
        # Collect first error cleanly
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(f"{field.capitalize()}: {error}")
        err_msg = "Transmission validation failed: " + "; ".join(error_list)

        if is_ajax:
            return JsonResponse({'status': 'error', 'message': err_msg, 'errors': form.errors}, status=400)
        messages.error(request, err_msg)
        return redirect('/#contact')
