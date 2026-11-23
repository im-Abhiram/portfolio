from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import ipaddress
from .models import NetworkKnowledgeTopic, SecurityTool, SecurityConcept


def lab_index_view(request):
    topics = NetworkKnowledgeTopic.objects.all()
    tools = SecurityTool.objects.all()
    concepts = SecurityConcept.objects.all()

    return render(request, 'lab/lab_index.html', {
        'topics': topics,
        'tools': tools,
        'concepts': concepts,
    })


def api_subnet_calc(request):
    """
    Defensive server-side validation and calculation API.
    Handles IPv4 and CIDR with strict O(1) memory bounds, preventing DoS/memory exhaustion.
    """
    ip_str = request.GET.get('ip', '192.168.10.0').strip()
    cidr_str = request.GET.get('cidr', '24').strip().lstrip('/')

    # Input length constraint to prevent ReDoS / memory attacks
    if len(ip_str) > 45 or len(cidr_str) > 5:
        return JsonResponse({'status': 'error', 'message': 'Input length exceeds permitted threshold'}, status=400)

    try:
        cidr_int = int(cidr_str)
        if not (0 <= cidr_int <= 32):
            return JsonResponse({'status': 'error', 'message': 'CIDR must be between 0 and 32'}, status=400)

        # Validate IP string format strictly before creating network
        try:
            ipaddress.IPv4Address(ip_str)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid IPv4 address format'}, status=400)

        network = ipaddress.IPv4Network(f"{ip_str}/{cidr_int}", strict=False)
        
        # Calculate usable hosts safely in O(1) memory WITHOUT generator expansion
        total_hosts = network.num_addresses
        if cidr_int == 32:
            usable_hosts = 1
            first_usable = str(network.network_address)
            last_usable = str(network.network_address)
        elif cidr_int == 31:
            usable_hosts = 2  # RFC 3021 Point-to-Point
            first_usable = str(network.network_address)
            last_usable = str(network.broadcast_address)
        else:
            usable_hosts = max(0, total_hosts - 2)
            first_usable = str(network.network_address + 1)
            last_usable = str(network.broadcast_address - 1)

        # Binary breakdown in O(1)
        binary_ip = '.'.join(f"{int(octet):08b}" for octet in str(network.network_address).split('.'))
        binary_mask = '.'.join(f"{int(octet):08b}" for octet in str(network.netmask).split('.'))

        # Wildcard mask calculation
        netmask_ints = [int(o) for o in str(network.netmask).split('.')]
        wildcard_ints = [255 - o for o in netmask_ints]
        wildcard_mask = '.'.join(str(o) for o in wildcard_ints)

        # Determine class safely
        first_octet = int(str(network.network_address).split('.')[0])
        if first_octet < 128:
            ip_class = 'Class A'
        elif first_octet < 192:
            ip_class = 'Class B'
        elif first_octet < 224:
            ip_class = 'Class C'
        elif first_octet < 240:
            ip_class = 'Class D (Multicast)'
        else:
            ip_class = 'Class E (Experimental)'

        return JsonResponse({
            'status': 'success',
            'data': {
                'network_address': str(network.network_address),
                'netmask': str(network.netmask),
                'wildcard_mask': wildcard_mask,
                'broadcast_address': str(network.broadcast_address),
                'cidr': f"/{cidr_int}",
                'total_hosts': total_hosts,
                'usable_hosts': usable_hosts,
                'first_usable': first_usable,
                'last_usable': last_usable,
                'ip_class': ip_class,
                'is_private': network.is_private,
                'binary_network': binary_ip,
                'binary_mask': binary_mask,
            }
        })
    except (ValueError, ipaddress.AddressValueError, ipaddress.NetmaskValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid IPv4 or CIDR parameter'}, status=400)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Internal subnet calculation failure'}, status=500)
