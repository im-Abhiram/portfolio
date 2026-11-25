# ABHIRAM ANIL — IT INFRASTRUCTURE & CYBERSECURITY PORTFOLIO
> **"Building, connecting and securing digital infrastructure."**
> A high-performance, dark-themed digital identity, network operations interface, and interactive engineering portfolio.

---

## 1. System Architecture & Overview

This project is a fully functional, production-ready portfolio web application engineered specifically for **Abhiram Anil**, an IT Executive and Cybersecurity Specialist based in Kerala, India. 

Designed with an aesthetic inspired by **Network Operations Centers (NOC)**, enterprise monitoring consoles, and minimal futuristic interfaces, the website bridges IT operations, network engineering, vulnerability auditing, and full-stack software development.

### Core Philosophy:
- **No Node.js / Webpack build step required**: Uses Vanilla JavaScript, HTML5 Canvas, modern CSS variables, and native Django templates.
- **PythonAnywhere Free Tier Compatible**: Optimized for zero-cost hosting with low CPU and memory footprints, persistent SQLite3 storage, WhiteNoise static compression, and standard WSGI handlers.
- **100% Resume-Accurate**: Every experience point, project, skill, and certification is directly derived from Abhiram's real background with zero invented claims.

---

## 2. Technology Stack

- **Backend**: Python 3.10+ / 3.14+, Django 5 / 6, SQLite3 database, Django ORM, Django Authentication & Session Engine, Django Admin.
- **Frontend**: HTML5, CSS3 Custom Properties, Vanilla JavaScript (ES6+), HTML5 Canvas Vector Physics, Bootstrap Icons (with graceful offline fallbacks), Google Fonts (`Space Grotesk`, `Inter`, `JetBrains Mono`).
- **Static & Media Serving**: WhiteNoise for high-efficiency asset compression and caching; Django Media storage for PDF resume distribution.
- **Security**: Django CSRF tokens, strict server-side form validation, honeypot anti-spam filters, IP-based sliding window rate-limiting, parameterized ORM queries, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`.

---

## 3. Directory Layout

```
D:\portfolio\
├── config/
│   ├── settings.py           # Production & development settings with env overrides
│   ├── urls.py               # Global routing, static/media handlers, custom 404/500
│   └── wsgi.py               # Standard WSGI entrypoint
├── core/
│   ├── models.py             # PortfolioSettings model (singleton HUD toggles)
│   ├── views.py              # Homepage, resume download stream, custom 404/500
│   ├── middleware.py         # SecurityHeadersMiddleware (CSP, Permissions-Policy, COOP, CORP)
│   ├── context_processors.py # Global site metadata and profile injector
│   ├── tests.py              # Full automated test suite (25 passing tests)
│   └── management/commands/
│       └── seed_portfolio.py # One-command database population script
├── portfolio/
│   ├── models.py             # Profile, Education, SkillCategory, Skill, Experience, Project, Certifications
│   ├── views.py              # Asynchronous JSON inspection APIs
│   └── urls.py               # API endpoints
├── lab/
│   ├── models.py             # NetworkKnowledgeTopic, SecurityTool, SecurityConcept
│   ├── views.py              # Subnet calculator API, lab view
│   └── urls.py               # Lab routes
├── journal/
│   ├── models.py             # BlogCategory, BlogPost, SecurityNote
│   ├── views.py              # Field notes archive and article reader
│   └── urls.py               # Journal routes
├── ai_services/
│   └── gemini.py             # Secure Gemini REST API v1beta client & model fallback
├── nexus/
│   ├── models.py             # Anonymized ChatUsageLog (rate/quota limiting, zero chat text)
│   ├── prompts.py            # Live portfolio-grounded system prompt + security guardrails
│   ├── views.py              # CSRF-protected POST chat API & status endpoints
│   └── tests.py              # Security, quota, error-handling, and validation tests
├── intelligence/
│   ├── models.py             # DailyArticle, ArticleGenerationLog, AISettings, IntelSubscriber
│   ├── topics.py             # Curated multi-category technical topic bank
│   ├── generator.py          # Idempotent article generation, validation & duplicate guard
│   ├── views.py              # Searchable/filterable archive, editorial reader & RSS feed
│   ├── management/commands/
│   │   └── generate_daily_article.py # Idempotent scheduled/manual CLI generator
│   └── tests.py              # Generation, dedup, portal workflow & view tests
├── portal/
│   ├── forms.py              # Operator Portal forms (Profile, Settings, DailyArticle, BlogPost)
│   ├── views.py              # Custom GUI admin views, CAPTCHA login, AI post editor
│   └── captcha.py            # Zero-dependency Pillow visual CAPTCHA engine
├── contact/
│   ├── models.py             # ContactMessage database model
│   ├── forms.py              # Honeypot-protected secure Django form
│   ├── views.py              # Rate-limited AJAX submission handler
│   └── urls.py               # Submission route
├── static/
│   ├── css/portfolio.css     # Complete NOC dark theme and responsive layout
│   └── js/
│       ├── main.js           # Theme toggle, scroll progress, navbar observer, AJAX form
│       ├── network-viz.js    # Hero Canvas network simulation with telemetry tooltips
│       ├── topology-explorer.js # Interactive enterprise topology & packet simulation
│       ├── subnet-calculator.js # Pure client-side IPv4/CIDR bitwise calculator
│       ├── osi-stack.js      # Interactive 7-layer visual stack explorer
│       ├── terminal.js       # Embedded interactive HUD CLI console
│       └── project-canvas.js # Mini canvas topology preview for Project 01
├── templates/
│   ├── base.html             # Base layout, HUD navbar, loader, terminal modal
│   ├── core/index.html       # Single-page scrolling portfolio with all sections
│   ├── core/404.html         # Network-inspired "Host Unreachable" 404 page
│   ├── core/500.html         # "Gateway Exception" 500 error page
│   ├── journal/              # Field notes archive and post detail templates
│   └── lab/                  # Standalone lab templates
├── media/                    # Uploaded resumes, project diagrams, and certs
├── staticfiles/              # Collected static files generated by collectstatic
├── pythonanywhere_wsgi.py     # Ready-to-use PythonAnywhere WSGI configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variable template
└── manage.py                 # Django management utility
```

---

## 4. Local Development Setup

### Step 1: Clone or Navigate to the Repository
```powershell
cd d:\portfolio
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```powershell
python manage.py migrate
```

### Step 4: Seed the Portfolio Database
Populate the database with all of Abhiram's real resume data, skills, experiences, projects, networking topics, and security concepts:
```powershell
python manage.py seed_portfolio
```

### Step 5: Start the Development Server
```powershell
python manage.py runserver
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 5. PythonAnywhere Free Account Deployment & Update Guide

This project is tailored specifically for PythonAnywhere's free account (`abhiramportfolio.pythonanywhere.com`).

---

### Part A: Initial First-Time Deployment Setup

#### 1. Clone Project Files
Log in to your PythonAnywhere account (`abhiramportfolio`) and open a **Bash Console**:
```bash
# Clone the repository directly into your home directory:
cd ~
git clone https://github.com/im-Abhiram/portfolio.git portfolio
cd ~/portfolio
```

#### 2. Create and Activate Virtual Environment
```bash
mkvirtualenv --python=python3.10 portfolio-venv
cd ~/portfolio
pip install -r requirements.txt
```

#### 3. Run Migrations & Seed Data
```bash
python manage.py migrate
python manage.py seed_portfolio
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### 4. Configure PythonAnywhere Web Tab
Navigate to the **Web** tab in PythonAnywhere dashboard:
1. Click **Add a new web app** -> Select **Manual configuration** -> Select **Python 3.10** (or installed Python 3.x).
2. **Code Section**:
   - **Source code**: `/home/abhiramportfolio/portfolio`
   - **Working directory**: `/home/abhiramportfolio/portfolio`
   - **WSGI configuration file**: Click the link to edit and paste the contents of `pythonanywhere_wsgi.py` (which already has `username = 'abhiramportfolio'`).
3. **Virtualenv Section**:
   - Set path to: `/home/abhiramportfolio/.virtualenvs/portfolio-venv`
4. **Static Files Section**:
   Add the following mappings:
   - **URL**: `/static/` &rarr; **Directory**: `/home/abhiramportfolio/portfolio/staticfiles`
   - **URL**: `/media/` &rarr; **Directory**: `/home/abhiramportfolio/portfolio/media`
5. Click **Reload abhiramportfolio.pythonanywhere.com**.

Your portfolio is now live at **[https://abhiramportfolio.pythonanywhere.com](https://abhiramportfolio.pythonanywhere.com)** with zero hosting fees!

---

### Part B: Updating the Web App with Latest GitHub Commits

Whenever you push new changes, bug fixes, or features to your GitHub repository (`main` branch), use any of the methods below to update your live PythonAnywhere site.

#### Method 1: Instant 1-Line Update (Fastest & Recommended)
Open a **Bash Console** in PythonAnywhere and paste this single command:
```bash
cd ~/portfolio && source ~/.virtualenvs/portfolio-venv/bin/activate && git pull origin main && pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput && touch /var/www/abhiramportfolio_pythonanywhere_com_wsgi.py
```
This automatically pulls your code, updates packages, migrates the database, refreshes static files, and reloads your web app in seconds!

#### Method 2: Using the Included Shell Script (`update_pa.sh`)
Inside your PythonAnywhere Bash Console:
```bash
cd ~/portfolio
bash update_pa.sh
```

#### Method 3: Step-by-Step Manual Update
If you prefer running each step individually:
```bash
# 1. Navigate to the repository
cd ~/portfolio

# 2. Activate virtual environment
workon portfolio-venv

# 3. Pull latest code from GitHub
git pull origin main

# 4. Install any new dependencies
pip install -r requirements.txt

# 5. Apply any database migrations
python manage.py migrate

# 6. Collect updated static assets (CSS, JS, images)
python manage.py collectstatic --noinput

# 7. Reload the live web application
touch /var/www/abhiramportfolio_pythonanywhere_com_wsgi.py
# (Or click the green 'Reload abhiramportfolio.pythonanywhere.com' button in the Web tab)
```

#### Verification After Updating:
1. Open your live website: **[https://abhiramportfolio.pythonanywhere.com](https://abhiramportfolio.pythonanywhere.com)**
2. Do a hard refresh in your browser (`Ctrl + F5` or `Cmd + Shift + R`) to bypass cached CSS/JS.
3. Access your operator portal: **[https://abhiramportfolio.pythonanywhere.com/portal/login/](https://abhiramportfolio.pythonanywhere.com/portal/login/)** to check visitor messages and make live edits.

---

## 6. NOC Operator Portal & CMS (`/portal/`)

The application includes a dedicated, dark NOC-themed **Operator Management Portal** accessible at `/portal/` (or via the link in the footer, or by typing `admin` in the terminal CLI).

### Key Features of the Operator Portal:
1. **Secure Authentication (`/portal/login/`)**:
   - Operator login restricted to staff accounts (`is_staff=True`).
   - Log in using the superuser account created with `python manage.py createsuperuser`.
2. **Visitor Transmissions Inbox (`/portal/messages/`)**:
   - Real-time review of all messages submitted through the website's contact form.
   - Shows sender Name, Email, Subject, Timestamp, and origin IP address.
   - Filter by All, Unread, or Read messages.
   - Instant message preview modal, one-click `mailto:` reply button, read/unread toggle, and message deletion.
3. **Live Main Page Content Editor (`/portal/profile/`)**:
   - Update your Full Name, Professional Title, Hero Headline, Secondary Statement, and About Me narrative directly without touching code or database shells.
   - Update contact coordinates (Email, Mobile Phone, Location, Timezone) and upload a new profile portrait photo.
4. **Site Settings & HUD Controls (`/portal/settings/`)**:
   - Manage the browser title (`<title>`), Brand Tagline, and NOC status text.
   - Upload a new PDF/DOCX resume file and customize the download filename.
   - Enable or disable specific portfolio sections on the fly (Lab section, Certifications, Field Notes, Terminal CLI).
5. **Network Intelligence & Field Notes Management (`/portal/intelligence/` & `/portal/journal/`)**:
   - Trigger **Generate Today's Article** manually, regenerate failed attempts, approve & publish (`Pending Review` &rarr; `Published`), unpublish, archive, or delete articles.
   - **Full Post Editor**: Edit any structured section of AI-generated `DailyArticle` briefings (or `BlogPost` field notes) cleanly through forms.
   - **Generation Logs & Topic Bank**: Review past API runs, token usage, errors, and unused topics.
   - **Offline JSON Import (`/portal/intelligence/import/`)**: Paste JSON generated locally if PythonAnywhere free outbound network restricts Gemini.
   - **Gemini AI Config (`/portal/ai-settings/`)**: Configure publishing mode (`review`, `auto`, `manual`), visitor daily quotas, and chatbot toggle without exposing `GEMINI_API_KEY`.
6. **Portfolio Data Management**:
   - **Projects (`/portal/projects/`)**: Add, edit, or delete deployed applications, live links, and GitHub repositories.
   - **Skills Matrix (`/portal/skills/`)**: Add, edit, or categorize networking, sysadmin, cybersecurity, and software skills.
   - **Certifications (`/portal/certifications/`)**: Add or edit accredited industry credentials.
   - **Experience (`/portal/experience/`)**: Manage career timeline and responsibilities.
6. **Advanced ORM Administration**:
   - Direct link to Django's low-level admin at `/admin/` for advanced database administration.

---

## 7. Page Structure & Interactive Flow

The web application is arranged in a logical narrative flow spanning 10 sections:
1. `#home` — **Hero Introduction**: NOC status indicators, personal branding, live telemetry ribbon, and interactive vector network topology simulator.
2. `#about` — **Digital Identity & Profile**: Verified portrait, professional narrative, contact coordinates, and B.Tech CSE academic credentials.
3. `#skills` — **Technical Competencies**: Interactive filter bar and categorized matrix (Network Engineering, System Administration, Cybersecurity, Software, Media).
4. `#experience` — **Operational Experience & Timeline**: Enterprise IT Executive responsibilities, Cybersecurity Internship, and academic milestones.
5. `#projects` — **Projects Showcase**: 8 full-stack and mobile applications with direct **Deployed App** launch buttons and GitHub source repositories.
6. `#certifications` — **Accredited Certifications**: 11 verified industry credentials (OCSP, Google Cyber Security, Cisco, etc.).
7. `#field-notes` — **Technical Field Notes**: Deep-dive technical articles and engineering research.
8. `#security` — **Defensive Security Operations**:
   - **Defensive Security Concepts Module**: OWASP Top 10 breakdown with threat severity tags, root causes, exploitation impacts, and SIEM/WAF detection strategies.
   - **Defensive Engineering & Vulnerability Assessment**: 8-tool auditing and reconnaissance toolchain.
   - **Activity Wall & Lab Observations**: Operational journal of laboratory exercises.
9. `#lab` — **Network & Infrastructure Lab**:
   - **OSI 7-Layer Visual Diagnostic Stack**: Interactive L1-L7 layer inspection with PDUs, standard protocols, devices, and troubleshooting scenarios.
   - **Networking Knowledge Explorer**: 18 protocol/architecture exploration cards with deep inspect modals.
   - **Interactive Network & Infrastructure Lab**: Enterprise VLAN architecture with simulated packet traversal and node telemetry drawer.
   - **Interactive IPv4 Subnetting Engine**: Pure bitwise subnet calculation engine with CIDR presets and binary breakdown.
10. `#contact` — **Initiate Contact**: Direct email, mobile number with one-click copy, verified social & professional channels (GitHub, LinkedIn, Instagram), and rate-limited secure transmission channel.

> **Navbar Sequence**: `Home` &rarr; `About` &rarr; `Skills` &rarr; `Experience` &rarr; `Projects` &rarr; `Certifications` &rarr; `Security` &rarr; `Infra Lab` &rarr; `Contact`.

---

## 7. Portfolio Features & Interactive Modules

### A. Verified Social & Developer Profiles
- **GitHub**: [https://github.com/im-Abhiram](https://github.com/im-Abhiram)
- **LinkedIn**: [https://www.linkedin.com/in/imabhiram/](https://www.linkedin.com/in/imabhiram/)
- **Instagram**: [https://www.instagram.com/im_abhiram__/](https://www.instagram.com/im_abhiram__/)
- **Email**: [abhiramanil74@gmail.com](mailto:abhiramanil74@gmail.com)
- **Phone**: `+91 9656537160` (Kerala, India)

### B. Hero Network Telemetry & Canvas
- Renders an interactive vector topology with nodes representing the **Internet Gateway**, **pfSense Firewall**, **Cisco Core Switch**, **Server Farm**, **Admin Workstations**, and **Security SIEM**.
- Hovering over any node calculates simulated ping latency and reveals active interface telemetry.
- Accessible pause/play button and native support for `prefers-reduced-motion`.

### B. Simulated Network Topology Explorer (Lab Section)
- Visualizes an enterprise campus architecture with **VLAN 10 (IT Management)**, **VLAN 20 (Corporate Admin)**, **VLAN 30 (Broadcast Production & Streaming)**, and **VLAN 40 (Guest Wireless)**.
- **Interactions**:
  - Filter by VLAN group.
  - Switch between **Logical View** and **Physical Rack View**.
  - Click any node to open the **Slide-out Node Inspector** showing IP assignments, interface speeds, and firewall policies.
  - Click **Simulate Packet Traversal** to trigger an animated ping sequence from an internal host through the Core Switch, pfSense Firewall, out to the Internet Gateway.
  - Explicitly labeled: *"Simulated Educational Model — Not actual workplace infrastructure"*.

### C. IPv4 & CIDR Subnet Calculator
- Pure Vanilla JavaScript engine executing bitwise operations on IPv4 addresses.
- Fast calculation of:
  - Network ID and Subnet Mask
  - Wildcard Mask
  - Broadcast Address
  - Usable Host Pool ($2^{(32 - CIDR)} - 2$)
  - First and Last Usable Host IPs
  - Address Class
  - Binary breakdown with visual highlighting of Network vs. Host bits.
- Handy preset buttons for `/24` Corporate LAN, `/26` Department, `/28` Server Farm, and `/30` WAN links.

### D. Networking Knowledge Explorer & OSI 7-Layer Stack
- 18 comprehensive topic cards (OSI, TCP/IP, IPv4, IPv6, Subnetting, CIDR, VLAN, Trunking, Routing, Switching, DHCP, DNS, NAT, ACL, Firewall, VPN, Wireless, Troubleshooting).
- Clicking any card opens a modal with: *Short Explanation*, *How It Works*, *Practical Enterprise Use*, *Troubleshooting Tip*, and *Relevant Diagnostic Tools*.
- Clickable 7-layer OSI visual stack displaying PDUs, protocols, hardware devices, and real-world failure scenarios.

### E. Cybersecurity Toolchain & Defensive Concepts
- 8 interactive tool cards: **Nmap**, **Wireshark**, **Burp Suite**, **Metasploit**, **Splunk**, **Gobuster**, **Netdiscover**, and **Hydra** detailing practical usage from Abhiram's internship.
- Defensive Concepts Accordion breaking down OWASP vulnerabilities: **SQLi**, **XSS**, **CSRF**, **Broken Access Control**, **SSRF**, **Command Injection**, and **Brute-Force Attacks** with root causes, impacts, code remediations, and SIEM detection ideas.

### F. Projects Showcase
The portfolio features 8 production-grade projects spanning network simulation, enterprise workforce management, manufacturing ERP, mobile Flutter applications, media news, real estate, and full-stack web platforms:
1. **Network Simulation Platform** (Python, Django, JavaScript, Canvas) — Interactive browser-based network simulation and CCNA education platform. [Deployed Webapp](https://ramonet.pythonanywhere.com/) | [GitHub](https://github.com/im-Abhiram/toolramo)
2. **Administrative Portal** (Python, Django, SQLite3, RBAC, Bootstrap) — Workforce management system with automated attendance, multi-cycle payroll calculation, shift-based overtime, and immutable audit logs. [Deployed Webapp](https://thamara.pythonanywhere.com/) | [GitHub](https://github.com/im-Abhiram/tempsite1)
3. **Production Tracking System** (Python, Django, SQLite3, Analytics) — Lightweight manufacturing & construction material ERP automating kiln shifts, live inventory formulas, dispatches, and credit ledgers. [Deployed Webapp](https://thamarayyathproduction.pythonanywhere.com/) | [GitHub](https://github.com/im-Abhiram/inventory)
4. **Remo** (Flutter, Dart, SQLite, On-Device OCR) — Premium offline-first Flutter application for intelligent receipt management, warranty alerts, EMI reminders, and private asset tracking. [GitHub](https://github.com/im-Abhiram/reme-doccument-remainder-app)
5. **6overnews** (Python, Django, SQLite3, Bootstrap) — Modern sports news website delivering real-time journalism, live fixtures, and league standings. [GitHub](https://github.com/im-Abhiram/6overnews-sports-news-website)
6. **Real Estate Web Application** (Python, Django, SQLite3, JS) — Real estate platform featuring property listings, multi-parameter search filters, and an agent inquiry dispatch system. [GitHub](https://github.com/im-Abhiram/real-estate-website)
7. **EASEFOOD** (Python, Django, SQLite3, Payment Integration) — Dynamic food commerce engine with real-time order status tracking and an administrative menu dashboard.
8. **Pet World** (Python, Django, SQLite, HTML5, CSS3, JS) — Full-stack MVT web app for pet adoption, rescue dispatch, veterinary appointments, and marketplace.

### G. Accredited Certifications
1. **Offenso Certified Security Professional (OCSP)** — Offenso Hackers Academy
2. **Google Cybersecurity Professional** — Coursera
3. **Cisco Networking Basics** — Cisco Networking Academy
4. **Introduction to Microsoft Excel** — Coursera
5. **Coding: Development & Advanced Engineering Job Simulation** — Accenture (Forage)
6. **Excel Skills Job Simulation** — JPMorgan Chase & Co. (Forage)
7. **Python for Data Science and Machine Learning** — Udemy
8. **Android Malware Analysis** — Udemy
9. **JavaScript for Beginners Complete Course** — Udemy
10. **CSS Crash Course for Beginners** — Udemy
11. **Mastering C & C++ Programming: From Fundamentals to Advanced** — Udemy

### H. Interactive HUD Terminal Console
- Accessible via the floating pill or keyboard shortcut (`` ` ``).
- Commands: `help`, `about`, `skills`, `network`, `security`, `projects`, `experience`, `certifications`, `subnet [ip/cidr]`, `ping [ip]`, `whoami`, `date`, `theme`, `clear`, `exit`.
- Features command history navigation (Up/Down arrows) and mobile-friendly command buttons.

### I. Django Admin Control Center
- Branded NOC interface for non-code management of:
  - Personal profile & biography
  - Skill categories and individual skills
  - Experience entries & responsibilities
  - Projects, architecture descriptions, and screenshots
  - Certifications & accreditation statuses
  - Contact messages (with read/unread triage)
  - Portfolio settings & downloadable resume document replacement.

---

## 8. Gemini AI Features & PythonAnywhere Scheduling

### A. NEXUS AI — Networking & Cybersecurity Assistant
- Floating dark graphite assistant accessible site-wide (stacked cleanly above the CLI Console pill so zero controls are covered).
- Powered server-side via Google Gemini REST API (`ai_services/gemini.py`) using `x-goog-api-key` headers — API credentials are never sent to the browser or exposed in HTML/JS.
- Grounds portfolio answers strictly on Abhiram Anil's live verified database profile while handling beginner, intermediate, and advanced networking, cybersecurity, sysadmin, and programming questions.
- Ephemeral client-side `sessionStorage` conversation history (never stored permanently in SQLite), safe DOM Markdown rendering (zero raw `innerHTML`), copy buttons for code & replies, and per-IP/session burst + daily quota rate limiting.

### B. NETWORK INTELLIGENCE — Automated Daily Article Publisher
- Dedicated publication interface at `#network-intelligence` and `/intelligence/` (`"One day. One concept. Better technical knowledge."`).
- Generates structured 16-part technical articles stored safely in `DailyArticle.content` (`JSONField`) and rendered with Django auto-escaping (no untrusted AI HTML execution).
- Covers 7 categories (`Networking`, `Network Security`, `Cybersecurity`, `System Administration`, `Web Application Security`, `IT Infrastructure`, `Python & Development`) with SHA-256 content hashing and similarity checks to prevent duplicates.
- Supports three publishing modes via `GEMINI_ARTICLE_PUBLISH_MODE`: `review` (default: saves as **Pending Review**), `auto` (publishes immediately), or `manual` (saves as **Draft**).

### C. Environment Configuration (`.env` / PythonAnywhere WSGI)
Configure these environment variables securely on the server (never commit `.env` to GitHub):
```env
GEMINI_API_KEY=your_secret_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_DAILY_ARTICLE_ENABLED=True
GEMINI_ARTICLE_PUBLISH_MODE=review
GEMINI_DAILY_REQUEST_LIMIT=10
GEMINI_CHAT_ENABLED=True
GEMINI_API_TIMEOUT=25
```

### D. Scheduling & PythonAnywhere Free Tier Compatibility
1. **Verify Outbound Access on PythonAnywhere**:
   PythonAnywhere free accounts route outbound HTTP traffic through an allowlist. Run a quick test in the PythonAnywhere **Bash Console**:
   ```bash
   cd ~/portfolio && workon portfolio-venv && python manage.py generate_daily_article --dry-run
   ```
   If live generation returns a proxy/connection restriction for `generativelanguage.googleapis.com`, request its addition via PythonAnywhere's Help / Allowlist Request form, **or use the built-in Offline Import Fallback**:
   - Run locally: `python manage.py generate_daily_article --export-json today.json`
   - Paste/import `today.json` in `/portal/intelligence/import/`.
2. **Automated Daily Schedule (Tasks Tab)**:
   If scheduled tasks are enabled on your PythonAnywhere account, add a daily task in the **Tasks** tab:
   ```bash
   /home/abhiramportfolio/.virtualenvs/portfolio-venv/bin/python /home/abhiramportfolio/portfolio/manage.py generate_daily_article
   ```
   The command is strictly idempotent (`Asia/Kolkata` timezone by default): running it multiple times on the same date never duplicates or overwrites a published article.
3. **Manual Admin Button Fallback**:
   If scheduled tasks are unavailable on your free tier, click **Generate Today's Article** anytime inside `/portal/intelligence/`.

---

## 9. Security Controls & Defense-in-Depth

| Security Vector | Implementation & Defensive Mechanism |
| :--- | :--- |
| **Content Security Policy (CSP)** | Custom middleware enforcing strict `script-src`, `style-src`, `font-src`, `img-src`, and `frame-ancestors 'none'` |
| **Permissions Policy** | Browser hardware isolation: `camera=()`, `microphone=()`, `geolocation=()`, `payment=()`, `usb=()` |
| **Clickjacking & Framing** | Dual-layer defense: `X-Frame-Options: DENY` and CSP `frame-ancestors 'none'` |
| **MIME Sniffing** | `X-Content-Type-Options: nosniff` |
| **Referrer Leakage** | `Referrer-Policy: strict-origin-when-cross-origin` |
| **Cross-Origin Isolation** | `Cross-Origin-Opener-Policy: same-origin-allow-popups` and `Cross-Origin-Resource-Policy: same-origin` |
| **CSRF Protection** | Django `CsrfViewMiddleware` with `SameSite=Lax` cookie flags |
| **Anti-Spam & Bot Defense** | Hidden honeypot field (`website_url`) rejecting automated bot payloads |
| **Dual-Layer Rate Limiting** | Sliding window rate limiter (max 5 transmissions / 15 mins) plus session-level rapid flood throttle |
| **IP Spoofing Defense** | Strict syntax validation of client IP addresses via `ipaddress` library before rate evaluation |
| **Header Injection Defense** | Contact form strips and rejects carriage return (`\r`) and newline (`\n`) characters in email and subject |
| **Subnet API DoS Immunity** | $O(1)$ memory address calculations eliminating generator list expansion; immune to `/8` (16.7M host) memory exhaustion |
| **DOM XSS Elimination** | Terminal (`terminal.js`) and UI alerts (`main.js`) construct text nodes via `.textContent` without unsafe `innerHTML` |
| **Modal Data Sanitization** | Dynamic project modals execute client-side HTML escaping (`escapeHtml`) and URL validation (`sanitizeUrl`) |
| **Path Traversal Defense** | Resume file serving verifies requested paths remain strictly within canonical `MEDIA_ROOT` bounds |
| **SQL Injection** | Exclusively parameterized queries via Django ORM; zero raw string SQL concatenation |
| **Audit Log Immutability** | Contact message logs in Django Admin are strictly read-only (`has_add_permission=False`) |
| **AI Credential Isolation** | `GEMINI_API_KEY` loaded solely from server env (`.env` / WSGI), passed via header (`x-goog-api-key`), scrubbed from errors, never saved in DB or templates |
| **AI Input & Output Hardening** | Strict 32KB payload limit, 1500-char message cap, history capping, prompt-injection boundaries, zero shell/DB tool execution, safe DOM Markdown & escaped JSON template rendering |
| **AI Rate & Quota Protection** | SQLite-backed anonymized burst + daily visitor quota enforcement (`ChatUsageLog` stores zero prompt text) |

---

## 10. Verification & Test Suite

The automated test suite covers views, models, forms, security filters, rate limiting, DoS resistance, subnet calculator API, NEXUS AI error/quota handling, and NETWORK INTELLIGENCE generation/idempotency/editorial workflow.

Run all tests:
```powershell
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
.............................................................
----------------------------------------------------------------------
Ran 61 tests in 17.0s

OK
Destroying test database for alias 'default'...
```

---

## 9. License & Credits

- Designed and engineered for **Abhiram Anil**.
- Built with Python & Django.
