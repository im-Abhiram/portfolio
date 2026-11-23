/**
 * Mini Interactive Topology Canvas for Project 01 Card
 * Renders an interactive simulated switch, firewall, and endpoints with live packet dots.
 */

(function () {
  const canvas = document.getElementById('project-mini-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const wrapper = canvas.parentElement;
  let width, height;

  function resize() {
    const rect = wrapper.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
  }

  window.addEventListener('resize', resize);
  resize();

  const miniNodes = [
    { label: 'FW', xRatio: 0.22, yRatio: 0.35, color: '#F87171' },
    { label: 'SW', xRatio: 0.50, yRatio: 0.35, color: '#C4F56A' },
    { label: 'SRV', xRatio: 0.78, yRatio: 0.35, color: '#77D6A1' },
    { label: 'PC1', xRatio: 0.35, yRatio: 0.75, color: '#9BA69D' },
    { label: 'PC2', xRatio: 0.65, yRatio: 0.75, color: '#9BA69D' }
  ];

  const miniLinks = [
    { from: 0, to: 1 },
    { from: 1, to: 2 },
    { from: 1, to: 3 },
    { from: 1, to: 4 }
  ];

  let packets = [
    { linkIdx: 0, t: 0.2, speed: 0.012 },
    { linkIdx: 1, t: 0.6, speed: 0.014 },
    { linkIdx: 2, t: 0.4, speed: 0.010 },
    { linkIdx: 3, t: 0.8, speed: 0.011 }
  ];

  function draw() {
    ctx.clearRect(0, 0, width, height);

    // Draw links
    miniLinks.forEach(link => {
      const n1 = miniNodes[link.from];
      const n2 = miniNodes[link.to];
      ctx.beginPath();
      ctx.moveTo(n1.xRatio * width, n1.yRatio * height);
      ctx.lineTo(n2.xRatio * width, n2.yRatio * height);
      ctx.strokeStyle = '#29332C';
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    // Draw packets
    packets.forEach(p => {
      p.t += p.speed;
      if (p.t > 1) p.t = 0;

      const link = miniLinks[p.linkIdx];
      const n1 = miniNodes[link.from];
      const n2 = miniNodes[link.to];

      const px = n1.xRatio * width + (n2.xRatio * width - n1.xRatio * width) * p.t;
      const py = n1.yRatio * height + (n2.yRatio * height - n1.yRatio * height) * p.t;

      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#C4F56A';
      ctx.fill();
    });

    // Draw nodes
    miniNodes.forEach(node => {
      const nx = node.xRatio * width;
      const ny = node.yRatio * height;

      ctx.beginPath();
      ctx.arc(nx, ny, 14, 0, Math.PI * 2);
      ctx.fillStyle = '#171D19';
      ctx.strokeStyle = node.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.fill();

      ctx.font = '9px "JetBrains Mono", monospace';
      ctx.fillStyle = node.color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.label, nx, ny);
    });

    requestAnimationFrame(draw);
  }

  draw();
})();
