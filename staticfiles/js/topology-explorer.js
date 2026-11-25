/**
 * Network & Infrastructure Lab - Interactive Simulated Topology Explorer
 * Features: Logical/Physical Views, VLAN Filtering, Node Inspector, and Simulated Packet Traversal.
 */

(function () {
  const container = document.getElementById('topology-container');
  const svg = document.getElementById('topology-svg');
  if (!container || !svg) return;

  const inspector = document.getElementById('node-inspector');
  const inspectorTitle = document.getElementById('inspector-device-name');
  const inspectorType = document.getElementById('inspector-device-type');
  const inspectorRole = document.getElementById('inspector-role');
  const inspectorIP = document.getElementById('inspector-ip');
  const inspectorVlan = document.getElementById('inspector-vlan');
  const inspectorDesc = document.getElementById('inspector-desc');
  const inspectorStatus = document.getElementById('inspector-status');
  const inspectorClose = document.getElementById('inspector-close-btn');

  const filterBtns = document.querySelectorAll('.lab-filter-btn');
  const viewToggleBtn = document.getElementById('topo-view-toggle');
  const packetSimBtn = document.getElementById('topo-sim-packet');
  const resetBtn = document.getElementById('topo-reset-btn');

  let currentView = 'logical'; // 'logical' or 'physical'
  let activeVlanFilter = 'all';
  let selectedNodeId = null;
  let isTraversing = false;

  // Simulated Nodes Data
  const topoNodes = [
    {
      id: 'node-inet',
      name: 'Internet Gateway',
      type: 'BGP Edge Router',
      role: 'Upstream Transit Provider',
      ip: '203.0.113.1 / 0.0.0.0/0',
      vlan: 'WAN',
      vlanGroup: 'wan',
      desc: 'Simulated border gateway connecting to upstream ISP transit with BGP routing.',
      status: 'LINK_UP // 10 Gbps SFP+',
      xLogical: 450, yLogical: 45,
      xPhysical: 450, yPhysical: 45,
      iconText: 'WAN',
      color: '#38BDF8'
    },
    {
      id: 'node-pfsense',
      name: 'Firewall',
      type: 'Stateful Security Appliance',
      role: 'Perimeter Defense & NAT',
      ip: 'WAN: 203.0.113.2 | LAN: 192.168.1.1/24',
      vlan: 'Trunk (802.1Q)',
      vlanGroup: 'infra',
      desc: 'Dual-homed stateful firewall enforcing inter-VLAN ACLs, NAT port forwarding, and intrusion prevention.',
      status: 'OPERATIONAL // 0.8% CPU',
      xLogical: 450, yLogical: 135,
      xPhysical: 450, yPhysical: 130,
      iconText: 'FW',
      color: '#F87171'
    },
    {
      id: 'node-cisco-core',
      name: 'Switch',
      type: 'Layer 3 Managed Switch',
      role: 'Core Distribution & Routing',
      ip: '192.168.1.2 / Management: VLAN 10',
      vlan: 'Trunk (802.1Q Native 999)',
      vlanGroup: 'infra',
      desc: 'High-availability switch distributing departmental VLANs.',
      status: 'LINK_UP // STP ROOT BRIDGE',
      xLogical: 450, yLogical: 240,
      xPhysical: 450, yPhysical: 225,
      iconText: 'L3',
      color: '#C4F56A'
    },
    {
      id: 'node-vlan10-srv',
      name: 'Active Directory Domain Controller',
      type: 'Windows Server 2022',
      role: 'Identity & DNS Server',
      ip: '192.168.10.10/24 (Static)',
      vlan: 'VLAN 10 – IT Management',
      vlanGroup: 'vlan10',
      desc: 'Centralized directory services, Kerberos authentication, and internal DNS resolution.',
      status: 'ONLINE // AD DS & DNS ACTIVE',
      xLogical: 140, yLogical: 390,
      xPhysical: 200, yPhysical: 340,
      iconText: 'AD',
      color: '#77D6A1'
    },
    {
      id: 'node-vlan10-jump',
      name: 'IT SysAdmin Jumpbox',
      type: 'Hardened Workstation',
      role: 'Management Bastion',
      ip: '192.168.10.15/24',
      vlan: 'VLAN 10 – IT Management',
      vlanGroup: 'vlan10',
      desc: 'Secure management station with SSH and RDP keys for administering network switches and firewalls.',
      status: 'ONLINE // MFA ENFORCED',
      xLogical: 250, yLogical: 470,
      xPhysical: 200, yPhysical: 430,
      iconText: 'MGT',
      color: '#77D6A1'
    },
    {
      id: 'node-vlan20-pc',
      name: 'Corporate Office Workstation',
      type: 'Domain Joined PC',
      role: 'Administration Staff Endpoint',
      ip: '192.168.20.25/24 (DHCP)',
      vlan: 'VLAN 20 – Administration',
      vlanGroup: 'vlan20',
      desc: 'Standard administrative workstation isolated from production broadcast streams and management interfaces.',
      status: 'ONLINE // GPO POLICY APPLIED',
      xLogical: 450, yLogical: 470,
      xPhysical: 450, yPhysical: 390,
      iconText: 'ADM',
      color: '#9BA69D'
    },
    {
      id: 'node-vlan30-stream',
      name: 'Broadcast Ingest Server',
      type: 'Broadcast Media Server',
      role: 'Wirecast / OBS Stream Ingest',
      ip: '192.168.30.50/24 (Static QoS)',
      vlan: 'VLAN 30 – Production / Broadcast',
      vlanGroup: 'vlan30',
      desc: 'Low-latency live broadcast ingest pipeline with dedicated bandwidth priority.',
      status: 'INGESTING // 1080p60 6500kbps',
      xLogical: 650, yLogical: 470,
      xPhysical: 700, yPhysical: 340,
      iconText: 'INGEST',
      color: '#E5A84B'
    },
    {
      id: 'node-vlan40-ap',
      name: 'Enterprise Access Point',
      type: '802.11ax Wi-Fi 6 AP',
      role: 'Guest & Mobile Wireless',
      ip: '192.168.40.100/24',
      vlan: 'VLAN 40 – Guest Wireless',
      vlanGroup: 'vlan40',
      desc: 'Isolated wireless access point with client isolation enabled. Direct routing to WAN only.',
      status: 'BROADCASTING // WPA3 ACTIVE',
      xLogical: 780, yLogical: 390,
      xPhysical: 700, yPhysical: 430,
      iconText: 'WLAN',
      color: '#38BDF8'
    }
  ];

  // Simulated Links
  const topoLinks = [
    { id: 'link-inet-pf', from: 'node-inet', to: 'node-pfsense', label: 'WAN Transit (1Gbps)', vlanGroup: 'wan' },
    { id: 'link-pf-cisco', from: 'node-pfsense', to: 'node-cisco-core', label: '802.1Q Trunk (LACP 2x10G)', vlanGroup: 'infra' },
    { id: 'link-cisco-v10-srv', from: 'node-cisco-core', to: 'node-vlan10-srv', label: 'Access Port (VLAN 10)', vlanGroup: 'vlan10' },
    { id: 'link-cisco-v10-jump', from: 'node-cisco-core', to: 'node-vlan10-jump', label: 'Access Port (VLAN 10)', vlanGroup: 'vlan10' },
    { id: 'link-cisco-v20-pc', from: 'node-cisco-core', to: 'node-vlan20-pc', label: 'Access Port (VLAN 20)', vlanGroup: 'vlan20' },
    { id: 'link-cisco-v30-stream', from: 'node-cisco-core', to: 'node-vlan30-stream', label: 'Access Port (VLAN 30 QoS)', vlanGroup: 'vlan30' },
    { id: 'link-cisco-v40-ap', from: 'node-cisco-core', to: 'node-vlan40-ap', label: 'Access Port (VLAN 40)', vlanGroup: 'vlan40' }
  ];

  function renderTopology() {
    svg.innerHTML = '';

    // Create defs for gradients and markers
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    defs.innerHTML = `
      <filter id="glow-filter" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
      </filter>
    `;
    svg.appendChild(defs);

    const linksGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    linksGroup.setAttribute('id', 'topo-links-group');
    svg.appendChild(linksGroup);

    const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    nodesGroup.setAttribute('id', 'topo-nodes-group');
    svg.appendChild(nodesGroup);

    // 1. Draw Links
    topoLinks.forEach(link => {
      const fromNode = topoNodes.find(n => n.id === link.from);
      const toNode = topoNodes.find(n => n.id === link.to);
      if (!fromNode || !toNode) return;

      const isVisible = activeVlanFilter === 'all' || 
                        link.vlanGroup === activeVlanFilter || 
                        link.vlanGroup === 'infra' || 
                        link.vlanGroup === 'wan';

      const x1 = currentView === 'logical' ? fromNode.xLogical : fromNode.xPhysical;
      const y1 = currentView === 'logical' ? fromNode.yLogical : fromNode.yPhysical;
      const x2 = currentView === 'logical' ? toNode.xLogical : toNode.xPhysical;
      const y2 = currentView === 'logical' ? toNode.yLogical : toNode.yPhysical;

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('id', link.id);
      line.setAttribute('x1', x1);
      line.setAttribute('y1', y1);
      line.setAttribute('x2', x2);
      line.setAttribute('y2', y2);
      line.setAttribute('class', `topology-link ${isVisible ? '' : 'faded-link'}`);
      line.style.opacity = isVisible ? '1' : '0.15';
      linksGroup.appendChild(line);
    });

    // 2. Draw Nodes
    topoNodes.forEach(node => {
      const isVisible = activeVlanFilter === 'all' || 
                        node.vlanGroup === activeVlanFilter || 
                        node.vlanGroup === 'infra' || 
                        node.vlanGroup === 'wan';

      const x = currentView === 'logical' ? node.xLogical : node.xPhysical;
      const y = currentView === 'logical' ? node.yLogical : node.yPhysical;

      const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      nodeGroup.setAttribute('class', 'topology-node-group');
      nodeGroup.setAttribute('data-id', node.id);
      nodeGroup.style.opacity = isVisible ? '1' : '0.2';
      nodeGroup.style.cursor = 'pointer';

      // Outer circle
      const outerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      outerCircle.setAttribute('cx', x);
      outerCircle.setAttribute('cy', y);
      outerCircle.setAttribute('r', '22');
      outerCircle.setAttribute('fill', '#171D19');
      outerCircle.setAttribute('stroke', selectedNodeId === node.id ? '#C4F56A' : node.color);
      outerCircle.setAttribute('stroke-width', selectedNodeId === node.id ? '3' : '1.8');
      if (selectedNodeId === node.id) {
        outerCircle.setAttribute('filter', 'url(#glow-filter)');
      }
      nodeGroup.appendChild(outerCircle);

      // Icon Text
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x);
      text.setAttribute('y', y + 4);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', node.color);
      text.setAttribute('font-family', 'JetBrains Mono, monospace');
      text.setAttribute('font-size', '10');
      text.setAttribute('font-weight', 'bold');
      text.textContent = node.iconText;
      nodeGroup.appendChild(text);

      // Label below
      const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', x);
      label.setAttribute('y', y + 36);
      label.setAttribute('text-anchor', 'middle');
      label.setAttribute('fill', selectedNodeId === node.id ? '#C4F56A' : '#E8EEE8');
      label.setAttribute('font-family', 'Space Grotesk, sans-serif');
      label.setAttribute('font-size', '11');
      label.setAttribute('font-weight', '600');
      label.textContent = node.name.length > 20 ? node.name.substring(0, 18) + '...' : node.name;
      nodeGroup.appendChild(label);

      // Click to open inspector
      nodeGroup.addEventListener('click', () => {
        selectNode(node);
      });

      nodesGroup.appendChild(nodeGroup);
    });
  }

  function selectNode(node) {
    selectedNodeId = node.id;
    renderTopology();

    // Populate inspector
    if (inspector) {
      inspector.classList.add('open');
      if (inspectorTitle) inspectorTitle.textContent = node.name;
      if (inspectorType) inspectorType.textContent = node.type;
      if (inspectorRole) inspectorRole.textContent = node.role;
      if (inspectorIP) inspectorIP.textContent = node.ip;
      if (inspectorVlan) inspectorVlan.textContent = node.vlan;
      if (inspectorDesc) inspectorDesc.textContent = node.desc;
      if (inspectorStatus) inspectorStatus.textContent = node.status;
    }

    highlightConnectedLinks(node.id);
  }

  function highlightConnectedLinks(nodeId) {
    document.querySelectorAll('.topology-link').forEach(link => {
      link.classList.remove('active-path');
    });

    topoLinks.forEach(link => {
      if (link.from === nodeId || link.to === nodeId) {
        const el = document.getElementById(link.id);
        if (el) el.classList.add('active-path');
      }
    });
  }

  if (inspectorClose) {
    inspectorClose.addEventListener('click', () => {
      inspector.classList.remove('open');
      selectedNodeId = null;
      renderTopology();
    });
  }

  // Filter Buttons
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeVlanFilter = btn.getAttribute('data-vlan');
      renderTopology();
    });
  });

  // Toggle View
  if (viewToggleBtn) {
    viewToggleBtn.addEventListener('click', () => {
      currentView = currentView === 'logical' ? 'physical' : 'logical';
      viewToggleBtn.innerHTML = currentView === 'logical' 
        ? '<i class="bi bi-diagram-3"></i> View: Logical' 
        : '<i class="bi bi-hdd-rack"></i> View: Physical';
      renderTopology();
    });
  }

  // Reset Button
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      activeVlanFilter = 'all';
      selectedNodeId = null;
      currentView = 'logical';
      if (viewToggleBtn) {
        viewToggleBtn.innerHTML = '<i class="bi bi-diagram-3"></i> View: Logical';
      }
      filterBtns.forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-vlan') === 'all');
      });
      if (inspector) inspector.classList.remove('open');
      renderTopology();
    });
  }

  // Simulate Packet Traversal: Workstation -> Switch -> Firewall -> Internet Gateway
  if (packetSimBtn) {
    packetSimBtn.addEventListener('click', () => {
      if (isTraversing) return;
      isTraversing = true;
      packetSimBtn.disabled = true;
      packetSimBtn.innerHTML = '<i class="bi bi-broadcast"></i> Simulating Ping...';

      // Path: Workstation (VLAN 20) -> Core Switch -> pfSense Firewall -> Internet Gateway
      const pathNodes = ['node-vlan20-pc', 'node-cisco-core', 'node-pfsense', 'node-inet'];
      const pathLinks = ['link-cisco-v20-pc', 'link-pf-cisco', 'link-inet-pf'];

      // Highlight links sequentially
      let step = 0;
      function stepAnimation() {
        if (step < pathLinks.length) {
          const linkEl = document.getElementById(pathLinks[step]);
          if (linkEl) linkEl.classList.add('active-path');
          step++;
          setTimeout(stepAnimation, 500);
        } else {
          // Finished transmission
          setTimeout(() => {
            document.querySelectorAll('.topology-link').forEach(l => l.classList.remove('active-path'));
            packetSimBtn.disabled = false;
            packetSimBtn.innerHTML = '<i class="bi bi-play-circle"></i> Simulate Packet Traversal';
            isTraversing = false;
          }, 1200);
        }
      }

      stepAnimation();
    });
  }

  // Initial render
  renderTopology();
})();
