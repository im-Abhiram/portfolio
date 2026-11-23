/**
 * Interactive HUD Terminal Emulator
 * Client-side CLI simulation for exploring Abhiram Anil's digital identity.
 */

(function () {
  const terminalBackdrop = document.getElementById('terminal-modal');
  const terminalBody = document.getElementById('terminal-output');
  const terminalInput = document.getElementById('terminal-input');
  const openTrigger = document.getElementById('open-terminal-btn');
  const navTrigger = document.getElementById('nav-terminal-btn');
  const closeBtn = document.getElementById('terminal-close-btn');
  const quickCmdBtns = document.querySelectorAll('.term-cmd-btn');

  if (!terminalInput || !terminalBody) return;

  const commandHistory = [];
  let historyIndex = -1;

  const welcomeBanner = `
======================================================================
  ABHIRAM ANIL // IT INFRASTRUCTURE & CYBERSECURITY TERMINAL v2.6.4
  Host: noc-console.local | Architecture: x86_64 | OS: GNU/Linux
  Type "help" to list available commands or click quick actions below.
======================================================================
`;

  const commands = {
    help: `
AVAILABLE COMMANDS:
  about           - Display professional identity & career background
  skills          - List core competencies across IT, Sec, & DevOps
  network         - Overview of network engineering & Cisco/pfSense focus
  security        - Cybersecurity toolchain & vulnerability analysis
  projects        - Key software & infrastructure projects
  experience      - Career timeline (JAIHIND TV, Offenso Hackers Academy)
  certifications  - Industry credentials & accredited certificates
  subnet [ip/cid] - Run inline subnet calculations (e.g. subnet 192.168.1.0/24)
  ping [target]   - Simulate ICMP echo requests to target host
  contact         - Reach out via email or direct transmission channel
  social          - View GitHub, LinkedIn, and Instagram channels
  github          - Open GitHub profile directly in new tab
  linkedin        - Open LinkedIn profile directly in new tab
  instagram       - Open Instagram profile directly in new tab
  admin           - Launch NOC Operator Admin Login Portal
  whoami          - Current session user identity
  date            - Current system timestamp
  theme           - Toggle dark/light interface mode
  clear           - Clear terminal buffer
  exit            - Close terminal modal
`,

    about: `
[IDENTITY RECORD]
Name: Abhiram Anil
Location: Kerala, India
Phone: +91 9656537160
Email: abhiramanil74@gmail.com
GitHub: https://github.com/im-Abhiram
LinkedIn: https://www.linkedin.com/in/imabhiram/
Instagram: https://www.instagram.com/im_abhiram__/
Education: B.Tech in Computer Science and Engineering — A.P.J Abdul Kalam Technological University (April 2025)
Title: IT Executive | Network Infrastructure | Cybersecurity | System Administration
Headline: "Building, connecting and securing digital infrastructure."

"Cybersecurity-driven B.Tech (CSE) graduate. Currently serving as an IT Executive, managing
enterprise-level systems while pursuing specialized training in cybersecurity (threat intelligence,
incident response, and network security). Proven ability to bridge the gap between core IT operations
and security compliance, with a focus on mitigating vulnerabilities and hardening system architecture."
`,

    education: `
[ACADEMIC CREDENTIALS]
Degree: Bachelor of Technology in Computer Science and Engineering
Institution: A.P.J Abdul Kalam Technological University, Kerala, IN
Graduation Date: April 2025
Core Focus: Computer Networks, Operating Systems, Database Systems, System Security, Software Engineering
`,

    skills: `
[CORE SKILL ECOSYSTEM]
• Network Infrastructure: Cisco Switching (802.1Q), VLANs, pfSense, TCP/IP, Diagnostics
• System Administration: Windows Server, Active Directory, OUs, GPO, Hardware Triage
• Cybersecurity: Nmap, Wireshark, Burp Suite, Metasploit, Splunk, Gobuster, Netdiscover, Hydra
• Development: Python, Django, SQL, JavaScript, C
• Streaming Infrastructure: OBS Studio, Wirecast, RTMP, RTMPS broadcast ingest
`,

    network: `
[NETWORK INFRASTRUCTURE LAB]
Architecture: Simulated Enterprise Backbone
Perimeter: pfSense Stateful Packet Filter & NAT Translation
Switching: Cisco 3750 Layer 3 Switch with 802.1Q Tagged Trunks
VLAN Segmentation:
  - VLAN 10 (IT Management - 192.168.10.0/24)
  - VLAN 20 (Corporate Admin - 192.168.20.0/24)
  - VLAN 30 (Broadcast Production - 192.168.30.0/24)
  - VLAN 40 (Guest Wireless - 192.168.40.0/24)
`,

    security: `
[CYBERSECURITY & AUDITING OPERATIONS]
Internship: Offenso Hackers Academy (Aug 2025 – Feb 2026)
Focus Areas:
  • Network reconnaissance, port scanning & auditing (Nmap)
  • Controlled exploitation testing in lab environments (Metasploit)
  • Web application vulnerability assessments (Burp Suite)
  • Traffic dissection & packet anomaly analysis (Wireshark)
  • Defensive remediation of OWASP Top 10 (SQLi, XSS, CSRF, SSRF)
`,

    projects: `
[PROJECT REPOSITORY]
01. Network Simulation Platform (Python, Django, JavaScript)
    Browser-based simulation featuring topology canvas, rack layouts,
    packet flow engine, and Cisco IOS/Linux CLI emulators.
    Deployed Webapp: https://ramonet.pythonanywhere.com/
    GitHub: https://github.com/im-Abhiram/toolramo

02. Administrative Portal (Python, Django, SQLite3, RBAC, Bootstrap)
    Production workforce ERP with automated attendance, multi-cycle payroll,
    shift-based overtime, and immutable audit logs.
    Deployed Webapp: https://thamara.pythonanywhere.com/
    GitHub: https://github.com/im-Abhiram/tempsite1

03. Production Tracking System (Python, Django, SQLite3, Analytics)
    Lightweight manufacturing & construction material ERP for shifts,
    live inventory formulas, dispatches, and credit tracking.
    Deployed Webapp: https://thamarayyathproduction.pythonanywhere.com/
    GitHub: https://github.com/im-Abhiram/inventory

04. Remo (Flutter, Dart, SQLite, On-Device OCR)
    Offline-first intelligent receipt management, warranty alerts,
    EMI reminders, vehicle expenses, and private asset tracking.
    GitHub: https://github.com/im-Abhiram/reme-doccument-remainder-app

05. 6overnews (Python, Django, SQLite3, Bootstrap)
    Modern sports news platform with live match fixtures, league tables,
    and trending sports journalism widgets.
    GitHub: https://github.com/im-Abhiram/6overnews-sports-news-website

06. Real Estate Web Application (Python, Django, SQLite3, JS)
    Property listings platform with multi-parameter filter queries,
    high-res galleries, and agent contact leads.
    GitHub: https://github.com/im-Abhiram/real-estate-website

07. EASEFOOD (Python, Django, SQLite3, Payment Gateway)
    Food ordering web application with live order status tracking,
    secure transaction processing, and menu management.

08. Pet World (Python, Django, SQLite, HTML5, CSS3, JS)
    Full-stack MVT web app for pet adoption, rescue dispatch,
    veterinary appointments, and marketplace.
`,

    experience: `
[PROFESSIONAL TIMELINE]
1. JAIHIND TV — IT Executive (Nov 2025 – Present)
   Location: Thiruvananthapuram, India
   Scope: Cisco switching, pfSense firewalls, VLAN departmental isolation,
   Active Directory domain management, and RTMP/RTMPS broadcast streaming.

2. OFFENSO HACKERS ACADEMY — Cybersecurity Intern (Aug 2025 – Feb 2026)
   Location: Thiruvananthapuram, India
   Scope: Reconnaissance, Nmap network audits, Metasploit proof-of-concept
   testing, and Burp Suite HTTP interception for XSS/SQLi vulnerabilities.
`,

    certifications: `
[VERIFIED CERTIFICATIONS]
• OFFENSO CERTIFIED SECURITY PROFESSIONAL (OCSP) — Offenso Hackers Academy
• GOOGLE CYBER SECURITY PROFESSIONAL — Coursera
• CISCO NETWORKING BASICS — Cisco Networking Academy
• INTRODUCTION TO MICROSOFT EXCEL — Coursera
• CODING: DEVELOPMENT & ADVANCED ENGINEERING JOB SIMULATION — Accenture (Forage)
• EXCEL SKILLS JOB SIMULATION — JPMorgan Chase & Co. (Forage)
• PYTHON FOR DATA SCIENCE AND MACHINE LEARNING — Udemy
• ANDROID MALWARE ANALYSIS — Udemy
• JAVASCRIPT FOR BEGINNERS COMPLETE COURSE — Udemy
• CSS CRASH COURSE FOR BEGINNERS — Udemy
• MASTERING C & C++ PROGRAMMING: FROM FUNDAMENTALS TO ADVANCED — Udemy
`,

    contact: `
[COMMUNICATION CHANNELS]
Email: abhiramanil74@gmail.com
Phone: +91 9656537160
Location: Kerala, India
GitHub: https://github.com/im-Abhiram
LinkedIn: https://www.linkedin.com/in/imabhiram/
Instagram: https://www.instagram.com/im_abhiram__/
Direct Message: Use the interactive form at the bottom of the page or run "email" to copy.
`,

    social: `
[SOCIAL & PROFESSIONAL CHANNELS]
GitHub:    https://github.com/im-Abhiram
LinkedIn:  https://www.linkedin.com/in/imabhiram/
Instagram: https://www.instagram.com/im_abhiram__/
`,

    github: () => {
      window.open('https://github.com/im-Abhiram', '_blank');
      return 'Opening GitHub profile: https://github.com/im-Abhiram';
    },

    linkedin: () => {
      window.open('https://www.linkedin.com/in/imabhiram/', '_blank');
      return 'Opening LinkedIn profile: https://www.linkedin.com/in/imabhiram/';
    },

    instagram: () => {
      window.open('https://www.instagram.com/im_abhiram__/', '_blank');
      return 'Opening Instagram profile: https://www.instagram.com/im_abhiram__/';
    },

    whoami: `visitor@noc-guest [Role: Remote Observer | Permissions: Read-Only]`,

    date: () => new Date().toUTCString(),

    theme: () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('portfolio-theme', newTheme);
      return `Theme switched to: ${newTheme.toUpperCase()}`;
    }
  };

  function appendOutput(text, isCommand = false) {
    const line = document.createElement('div');
    line.className = 'term-output-line';
    if (isCommand) {
      const promptSpan = document.createElement('span');
      promptSpan.className = 'term-prompt-label';
      promptSpan.textContent = 'abhiram@noc:~$ ';

      const cmdSpan = document.createElement('span');
      cmdSpan.style.color = '#ffffff';
      cmdSpan.textContent = text;

      line.appendChild(promptSpan);
      line.appendChild(cmdSpan);
    } else {
      line.textContent = text;
    }
    terminalBody.appendChild(line);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }

  function handleCommand(rawCmd) {
    const cmdTrimmed = rawCmd.trim();
    if (!cmdTrimmed) return;

    commandHistory.push(cmdTrimmed);
    historyIndex = commandHistory.length;

    appendOutput(cmdTrimmed, true);

    const parts = cmdTrimmed.split(/\s+/);
    const mainCmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    if (mainCmd === 'clear') {
      while (terminalBody.firstChild) {
        terminalBody.removeChild(terminalBody.firstChild);
      }
      return;
    }

    if (mainCmd === 'exit') {
      if (terminalBackdrop) terminalBackdrop.classList.remove('open');
      return;
    }

    if (mainCmd === 'admin' || mainCmd === 'portal' || mainCmd === 'login') {
      appendOutput('[LAUNCHING SECURE NOC OPERATOR PORTAL]');
      setTimeout(() => {
        window.location.href = '/portal/login/';
      }, 500);
      return;
    }

    if (mainCmd === 'ping') {
      const target = args[0] || '192.168.1.1';
      appendOutput(`PING ${target} (56 data bytes):`);
      for (let i = 1; i <= 4; i++) {
        setTimeout(() => {
          const time = (Math.random() * 2 + 1).toFixed(2);
          appendOutput(`64 bytes from ${target}: icmp_seq=${i} ttl=64 time=${time} ms`);
        }, i * 300);
      }
      return;
    }

    if (mainCmd === 'subnet') {
      const targetSubnet = args[0] || '192.168.10.0/24';
      appendOutput(`[SUBNET ANALYSIS: ${targetSubnet}]`);
      appendOutput(`Network: 192.168.10.0 | Netmask: 255.255.255.0 | Hosts: 254 usable`);
      appendOutput(`First Host: 192.168.10.1 | Last Host: 192.168.10.254 | Broadcast: 192.168.10.255`);
      return;
    }

    if (commands[mainCmd]) {
      const res = typeof commands[mainCmd] === 'function' ? commands[mainCmd]() : commands[mainCmd];
      appendOutput(res);
    } else {
      appendOutput(`bash: command not found: ${mainCmd}. Type "help" for a list of valid commands.`);
    }
  }

  // Input Keydown Handler
  terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const val = terminalInput.value;
      terminalInput.value = '';
      handleCommand(val);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex > 0) {
        historyIndex--;
        terminalInput.value = commandHistory[historyIndex];
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex < commandHistory.length - 1) {
        historyIndex++;
        terminalInput.value = commandHistory[historyIndex];
      } else {
        historyIndex = commandHistory.length;
        terminalInput.value = '';
      }
    }
  });

  // Modal Open / Close
  function openTerminal() {
    if (terminalBackdrop) {
      terminalBackdrop.classList.add('open');
      if (terminalBody.children.length === 0) {
        appendOutput(welcomeBanner);
      }
      setTimeout(() => terminalInput.focus(), 150);
    }
  }

  function closeTerminal() {
    if (terminalBackdrop) terminalBackdrop.classList.remove('open');
  }

  if (openTrigger) openTrigger.addEventListener('click', openTerminal);
  if (navTrigger) navTrigger.addEventListener('click', openTerminal);
  if (closeBtn) closeBtn.addEventListener('click', closeTerminal);

  // Quick Command Buttons
  quickCmdBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      if (cmd) {
        terminalInput.value = '';
        handleCommand(cmd);
      }
    });
  });
})();
