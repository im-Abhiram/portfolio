/**
 * Interactive Hero Network Topology Visualizer
 * HTML5 Canvas rendering connected nodes with packet flow and interactive telemetry tooltips.
 */

(function () {
  const canvas = document.getElementById('hero-network-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const wrapper = canvas.parentElement;
  const tooltip = document.getElementById('hero-viz-tooltip');
  const toggleBtn = document.getElementById('hero-viz-toggle-btn');

  let animationId = null;
  let isPaused = false;
  let width, height;
  let hoveredNode = null;

  // Check prefers-reduced-motion
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (mediaQuery.matches) {
    isPaused = true;
    if (toggleBtn) toggleBtn.innerHTML = '<i class="bi bi-play-fill"></i> Play';
  }

  // Network Nodes Definition
  const nodes = [
    {
      id: 'internet',
      label: 'Internet Gateway',
      role: 'Upstream Transit / BGP Edge',
      ip: '203.0.113.1 (WAN Gateway)',
      type: 'gateway',
      xRatio: 0.18,
      yRatio: 0.22,
      radius: 20,
      color: '#38BDF8',
      pulse: 0
    },
    {
      id: 'firewall',
      label: 'pfSense Firewall',
      role: 'Stateful Filtering & NAT Edge',
      ip: '192.168.1.1 (Perimeter)',
      type: 'firewall',
      xRatio: 0.48,
      yRatio: 0.22,
      radius: 24,
      color: '#F87171',
      pulse: 0
    },
    {
      id: 'switch',
      label: 'Cisco Core Switch',
      role: '802.1Q Inter-VLAN Distribution',
      ip: '192.168.1.2 (L3 Core)',
      type: 'switch',
      xRatio: 0.48,
      yRatio: 0.58,
      radius: 26,
      color: '#C4F56A',
      pulse: 0
    },
    {
      id: 'servers',
      label: 'Server Farm / AD DC',
      role: 'Directory Services & Ingest',
      ip: '192.168.10.10 (VLAN 10)',
      type: 'server',
      xRatio: 0.20,
      yRatio: 0.82,
      radius: 22,
      color: '#77D6A1',
      pulse: 0
    },
    {
      id: 'workstations',
      label: 'Admin Workstations',
      role: 'Departmental Endpoints',
      ip: '192.168.20.50 (VLAN 20)',
      type: 'workstation',
      xRatio: 0.50,
      yRatio: 0.88,
      radius: 19,
      color: '#9BA69D',
      pulse: 0
    },
    {
      id: 'security',
      label: 'Security Monitoring / SIEM',
      role: 'Splunk & Packet Inspection',
      ip: '192.168.10.99 (Audit Tap)',
      type: 'security',
      xRatio: 0.82,
      yRatio: 0.58,
      radius: 22,
      color: '#E5A84B',
      pulse: 0
    }
  ];

  // Connections (Links) between Nodes
  const links = [
    { from: 'internet', to: 'firewall', speed: 0.007 },
    { from: 'firewall', to: 'switch', speed: 0.009 },
    { from: 'switch', to: 'servers', speed: 0.008 },
    { from: 'switch', to: 'workstations', speed: 0.006 },
    { from: 'switch', to: 'security', speed: 0.007 },
    { from: 'firewall', to: 'security', speed: 0.006 }
  ];

  // Simulated Packets traveling on links
  const packets = links.map(link => ({
    link,
    progress: Math.random(),
    reverse: Math.random() > 0.5
  }));

  function resizeCanvas() {
    const rect = wrapper.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    
    // Account for high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
  }

  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Mouse move detection for hover tooltips
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    hoveredNode = null;

    for (let node of nodes) {
      const nx = node.xRatio * width;
      const ny = node.yRatio * height;
      const dist = Math.hypot(mouseX - nx, mouseY - ny);

      if (dist <= node.radius + 6) {
        hoveredNode = node;
        break;
      }
    }

    if (hoveredNode && tooltip) {
      tooltip.style.display = 'block';
      tooltip.style.left = `${e.clientX - rect.left + 15}px`;
      tooltip.style.top = `${e.clientY - rect.top + 15}px`;
      tooltip.innerHTML = `
        <div class="viz-tooltip-name">${hoveredNode.label}</div>
        <div class="viz-tooltip-role">${hoveredNode.role}</div>
        <div style="font-size: 0.68rem; color: var(--accent-lime); margin-top: 4px;">
          IP: ${hoveredNode.ip}<br>
          LATENCY: ${Math.floor(Math.random() * 2 + 1)}ms // STATUS: ACTIVE
        </div>
      `;
    } else if (tooltip) {
      tooltip.style.display = 'none';
    }
  });

  canvas.addEventListener('mouseleave', () => {
    hoveredNode = null;
    if (tooltip) tooltip.style.display = 'none';
  });

  // Pause / Play toggle
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      isPaused = !isPaused;
      if (isPaused) {
        toggleBtn.innerHTML = '<i class="bi bi-play-fill"></i> Play';
        if (animationId) cancelAnimationFrame(animationId);
      } else {
        toggleBtn.innerHTML = '<i class="bi bi-pause-fill"></i> Pause';
        animate();
      }
    });
  }

  // Animation Loop
  function animate() {
    ctx.clearRect(0, 0, width, height);

    // 1. Draw Links
    links.forEach(link => {
      const fromNode = nodes.find(n => n.id === link.from);
      const toNode = nodes.find(n => n.id === link.to);
      if (!fromNode || !toNode) return;

      const x1 = fromNode.xRatio * width;
      const y1 = fromNode.yRatio * height;
      const x2 = toNode.xRatio * width;
      const y2 = toNode.yRatio * height;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = (hoveredNode && (hoveredNode.id === link.from || hoveredNode.id === link.to))
        ? 'rgba(196, 245, 106, 0.65)'
        : 'rgba(41, 51, 44, 0.7)';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    // 2. Draw Moving Packets
    if (!isPaused) {
      packets.forEach(p => {
        p.progress += p.link.speed;
        if (p.progress > 1) {
          p.progress = 0;
          p.reverse = !p.reverse;
        }

        const fromNode = nodes.find(n => n.id === p.link.from);
        const toNode = nodes.find(n => n.id === p.link.to);
        if (!fromNode || !toNode) return;

        const x1 = fromNode.xRatio * width;
        const y1 = fromNode.yRatio * height;
        const x2 = toNode.xRatio * width;
        const y2 = toNode.yRatio * height;

        const curT = p.reverse ? (1 - p.progress) : p.progress;
        const px = x1 + (x2 - x1) * curT;
        const py = y1 + (y2 - y1) * curT;

        ctx.beginPath();
        ctx.arc(px, py, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#C4F56A';
        ctx.shadowColor = '#C4F56A';
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0; // reset
      });
    }

    // 3. Draw Nodes
    nodes.forEach(node => {
      const nx = node.xRatio * width;
      const ny = node.yRatio * height;
      const isHovered = hoveredNode && hoveredNode.id === node.id;

      node.pulse += 0.03;
      const pulseSize = Math.sin(node.pulse) * 3;

      // Outer glow ring
      ctx.beginPath();
      ctx.arc(nx, ny, node.radius + pulseSize + (isHovered ? 4 : 0), 0, Math.PI * 2);
      ctx.fillStyle = isHovered ? 'rgba(196, 245, 106, 0.2)' : 'rgba(30, 39, 33, 0.4)';
      ctx.fill();

      // Node base circle
      ctx.beginPath();
      ctx.arc(nx, ny, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = '#171D19';
      ctx.strokeStyle = isHovered ? '#C4F56A' : node.color;
      ctx.lineWidth = isHovered ? 2.5 : 1.5;
      ctx.stroke();
      ctx.fill();

      // Inner status indicator
      ctx.beginPath();
      ctx.arc(nx, ny, 5, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();

      // Label below node
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.fillStyle = isHovered ? '#C4F56A' : '#9BA69D';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, nx, ny + node.radius + 16);
    });

    if (!isPaused) {
      animationId = requestAnimationFrame(animate);
    }
  }

  animate();
})();
