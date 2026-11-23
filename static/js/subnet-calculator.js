/**
 * Interactive IPv4 & CIDR Subnet Calculator
 * High-precision bitwise network calculations in Vanilla JavaScript.
 */

(function () {
  const ipInput = document.getElementById('calc-ip-input');
  const cidrSelect = document.getElementById('calc-cidr-select');
  const calcBtn = document.getElementById('calc-execute-btn');
  const errorMsg = document.getElementById('calc-error-msg');

  // Result display elements
  const resNetwork = document.getElementById('res-network');
  const resNetmask = document.getElementById('res-netmask');
  const resWildcard = document.getElementById('res-wildcard');
  const resBroadcast = document.getElementById('res-broadcast');
  const resTotalHosts = document.getElementById('res-total-hosts');
  const resUsableHosts = document.getElementById('res-usable-hosts');
  const resFirstUsable = document.getElementById('res-first-usable');
  const resLastUsable = document.getElementById('res-last-usable');
  const resClass = document.getElementById('res-class');
  const resBinaryNetwork = document.getElementById('res-binary-network');
  const resBinaryMask = document.getElementById('res-binary-mask');

  const presetBtns = document.querySelectorAll('.preset-pill');

  if (!ipInput || !cidrSelect) return;

  function parseIp(ipStr) {
    const parts = ipStr.trim().split('.');
    if (parts.length !== 4) return null;
    const octets = [];
    for (let part of parts) {
      if (!/^\d+$/.test(part)) return null;
      const num = parseInt(part, 10);
      if (num < 0 || num > 255) return null;
      octets.push(num);
    }
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3];
  }

  function intToIp(intVal) {
    return [
      (intVal >>> 24) & 255,
      (intVal >>> 16) & 255,
      (intVal >>> 8) & 255,
      intVal & 255
    ].join('.');
  }

  function intToBinaryStr(intVal, cidr) {
    let bits = (intVal >>> 0).toString(2).padStart(32, '0');
    // Group into 4 octets of 8 bits
    const octets = [];
    for (let i = 0; i < 32; i += 8) {
      octets.push(bits.slice(i, i + 8));
    }
    return octets.join('.');
  }

  function calculateSubnet() {
    if (errorMsg) errorMsg.style.display = 'none';

    const ipStr = ipInput.value.trim();
    const cidr = parseInt(cidrSelect.value, 10);

    const ipInt = parseIp(ipStr);
    if (ipInt === null) {
      showError('Invalid IPv4 address format. Please enter a valid dotted decimal address (e.g. 192.168.10.0).');
      return;
    }

    if (isNaN(cidr) || cidr < 0 || cidr > 32) {
      showError('CIDR prefix must be between /0 and /32.');
      return;
    }

    // Mask integer: e.g. /24 -> 32 - 24 = 8 zero bits
    const maskInt = cidr === 0 ? 0 : (~0 << (32 - cidr)) >>> 0;
    const wildcardInt = ~maskInt >>> 0;

    const networkInt = (ipInt & maskInt) >>> 0;
    const broadcastInt = (networkInt | wildcardInt) >>> 0;

    const totalHosts = Math.pow(2, 32 - cidr);
    let usableHosts = 0;
    let firstUsableInt = 0;
    let lastUsableInt = 0;

    if (cidr >= 31) {
      usableHosts = cidr === 31 ? 2 : 1;
      firstUsableInt = networkInt;
      lastUsableInt = broadcastInt;
    } else {
      usableHosts = Math.max(0, totalHosts - 2);
      firstUsableInt = (networkInt + 1) >>> 0;
      lastUsableInt = (broadcastInt - 1) >>> 0;
    }

    // IP Class determination
    const firstOctet = (ipInt >>> 24) & 255;
    let ipClass = 'Class A';
    if (firstOctet >= 128 && firstOctet <= 191) ipClass = 'Class B';
    else if (firstOctet >= 192 && firstOctet <= 223) ipClass = 'Class C';
    else if (firstOctet >= 224 && firstOctet <= 239) ipClass = 'Class D (Multicast)';
    else if (firstOctet >= 240) ipClass = 'Class E (Experimental)';

    // Update UI elements
    if (resNetwork) resNetwork.textContent = `${intToIp(networkInt)} /${cidr}`;
    if (resNetmask) resNetmask.textContent = intToIp(maskInt);
    if (resWildcard) resWildcard.textContent = intToIp(wildcardInt);
    if (resBroadcast) resBroadcast.textContent = intToIp(broadcastInt);
    if (resTotalHosts) resTotalHosts.textContent = totalHosts.toLocaleString();
    if (resUsableHosts) resUsableHosts.textContent = usableHosts.toLocaleString();
    if (resFirstUsable) resFirstUsable.textContent = intToIp(firstUsableInt);
    if (resLastUsable) resLastUsable.textContent = intToIp(lastUsableInt);
    if (resClass) resClass.textContent = ipClass;

    // Binary breakdown
    if (resBinaryNetwork) resBinaryNetwork.textContent = intToBinaryStr(networkInt, cidr);
    if (resBinaryMask) resBinaryMask.textContent = intToBinaryStr(maskInt, cidr);
  }

  function showError(msg) {
    if (errorMsg) {
      errorMsg.textContent = msg;
      errorMsg.style.display = 'block';
    }
  }

  // Event Listeners
  if (calcBtn) {
    calcBtn.addEventListener('click', calculateSubnet);
  }

  ipInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      calculateSubnet();
    }
  });

  cidrSelect.addEventListener('change', calculateSubnet);

  // Preset Buttons
  presetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const presetIp = btn.getAttribute('data-ip');
      const presetCidr = btn.getAttribute('data-cidr');
      if (presetIp && ipInput) ipInput.value = presetIp;
      if (presetCidr && cidrSelect) cidrSelect.value = presetCidr;
      calculateSubnet();
    });
  });

  // Calculate default initially
  calculateSubnet();
})();
