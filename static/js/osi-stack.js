/**
 * Interactive OSI 7-Layer Visual Stack Explorer
 * Enables clicking through the 7 networking layers to inspect PDUs, protocols, devices, and troubleshooting scenarios.
 */

(function () {
  const layerBtns = document.querySelectorAll('.osi-layer-btn');
  const titleEl = document.getElementById('osi-inspect-title');
  const pduEl = document.getElementById('osi-inspect-pdu');
  const funcEl = document.getElementById('osi-inspect-functions');
  const protoEl = document.getElementById('osi-inspect-protocols');
  const deviceEl = document.getElementById('osi-inspect-devices');
  const scenarioEl = document.getElementById('osi-inspect-scenario');

  if (!layerBtns.length) return;

  const osiData = {
    7: {
      name: 'Layer 7: Application Layer',
      pdu: 'Data',
      functions: 'Direct interface between end-user applications and underlying network services. Initiates and manages network requests.',
      protocols: 'HTTP, HTTPS, DNS, DHCP, SSH, FTP, SMTP, SNMP, Telnet',
      devices: 'Application Proxies, Web Application Firewalls (WAF), Load Balancers, API Gateways',
      scenarios: 'A user receives an HTTP 502 Bad Gateway or DNS NXDOMAIN. Bottom layers are functioning, but the application service daemon or upstream reverse proxy is down.'
    },
    6: {
      name: 'Layer 6: Presentation Layer',
      pdu: 'Data',
      functions: 'Data representation, syntax translation, encryption/decryption (TLS/SSL), and compression.',
      protocols: 'TLS/SSL, ASCII, UTF-8, JSON, XML, JPEG, MPEG, H.264 video compression',
      devices: 'TLS Termination Proxies, Encryption Appliances, Media Encoders (OBS / Wirecast)',
      scenarios: 'A client fails to negotiate a cipher suite during the TLS handshake, triggering SSL_ERROR_NO_CYPHER_OVERLAP. Verify certificate validity and cipher configurations.'
    },
    5: {
      name: 'Layer 5: Session Layer',
      pdu: 'Data',
      functions: 'Establishes, maintains, coordinates, and terminates communication sessions between local and remote applications.',
      protocols: 'NetBIOS, RPC, SMB, PPTP, SOCKS, SIP',
      devices: 'Session Border Controllers (SBC), RPC Gateways',
      scenarios: 'An SMB file share session disconnects intermittently due to keep-alive session timeouts across a stateful firewall. Check firewall session state expiration limits.'
    },
    4: {
      name: 'Layer 4: Transport Layer',
      pdu: 'Segments (TCP) / Datagrams (UDP)',
      functions: 'End-to-end transport communication, segment multiplexing via port numbers, error recovery, flow control, and windowing.',
      protocols: 'TCP, UDP, SCTP, QUIC (HTTP/3)',
      devices: 'Layer 4 Firewalls (pfSense), TCP/UDP Load Balancers',
      scenarios: 'Port scanning with Nmap shows port 443 filtered rather than open or closed. A firewall rule is silently dropping SYN packets without returning TCP RST.'
    },
    3: {
      name: 'Layer 3: Network Layer',
      pdu: 'Packets',
      functions: 'Logical addressing (IPv4/IPv6), path determination, packet routing, fragmentation, and packet forwarding across boundaries.',
      protocols: 'IPv4, IPv6, ICMP, IPsec, OSPF, BGP, EIGRP, ARP',
      devices: 'Routers, Layer 3 Switches (Cisco Catalyst), pfSense Gateways',
      scenarios: 'A host can ping its default gateway but cannot ping 8.8.8.8. The local interface is working, but the gateway lacks a valid default route (0.0.0.0/0) or NAT configuration.'
    },
    2: {
      name: 'Layer 2: Data Link Layer',
      pdu: 'Frames',
      functions: 'Physical addressing (MAC addresses), frame encapsulation, error detection (FCS/CRC), and local network media access control.',
      protocols: 'Ethernet (802.3), Wi-Fi (802.11), VLAN Trunking (802.1Q), STP (802.1D), LACP (802.3ad), PPP',
      devices: 'Layer 2 Managed Switches, Network Interface Cards (NICs), Wireless Access Points',
      scenarios: 'An endpoint receives a 169.254.x.x APIPA address. The physical link light is active, but the switch port is assigned to the wrong VLAN or 802.1Q trunk native VLAN is mismatched.'
    },
    1: {
      name: 'Layer 1: Physical Layer',
      pdu: 'Bits',
      functions: 'Unstructured raw bit stream transmission over physical mediums: electrical voltages, optical pulses, or radio frequencies.',
      protocols: '1000BASE-T, 10GBASE-SR, RJ45 Pinouts (T568B), Fiber Optic (LC/SC), RF Spectrum',
      devices: 'Patch Panels, CAT6 / Fiber Cables, SFP+ Transceivers, Repeaters, Network Hubs',
      scenarios: 'NIC link light is dark or flashing amber. Check for damaged CAT6 patch cables, bent pins in RJ45 modular jacks, or faulty SFP+ optical transceivers with a cable tester.'
    }
  };

  function displayLayer(layerNum) {
    const data = osiData[layerNum];
    if (!data) return;

    layerBtns.forEach(btn => {
      const num = parseInt(btn.getAttribute('data-layer'), 10);
      btn.classList.toggle('active', num === layerNum);
    });

    if (titleEl) titleEl.textContent = data.name;
    if (pduEl) pduEl.textContent = data.pdu;
    if (funcEl) funcEl.textContent = data.functions;
    if (protoEl) protoEl.textContent = data.protocols;
    if (deviceEl) deviceEl.textContent = data.devices;
    if (scenarioEl) scenarioEl.textContent = data.scenarios;
  }

  layerBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const num = parseInt(btn.getAttribute('data-layer'), 10);
      displayLayer(num);
    });
  });

  // Display Layer 7 by default
  displayLayer(7);
})();
