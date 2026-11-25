# Security Audit, Remediation & Verification Report

**Application:** Abhiram Anil Portfolio & NOC Operations Platform (Django + SQLite + Gemini AI)  
**Assessment Scope:** Source code audit, OWASP Top 10 remediation, Django deployment hardening, dependency review, Git/secret hygiene audit, and automated security regression testing.

---

## 1. Executive Summary

A full security audit and remediation pass was performed across all Django apps (`core`, `portfolio`, `lab`, `journal`, `contact`, `nexus`, `intelligence`, `portal`), AI service integration (`ai_services`), frontend templates/JavaScript, file upload handlers, WSGI/deployment configuration, and repository state.

All identified **High** and **Medium** code-level vulnerabilities were remediated directly in source files and verified using an expanded 71-test automated suite (10 new security regression tests in `core/security_tests.py` plus 61 preserved application/feature tests) and `python manage.py check --deploy` (`DJANGO_DEBUG=False`).

**Actionable Residual Items Requiring Owner Action (`NEEDS REVIEW`):**
1. **Rotate Secrets & Credentials:** Rotate `GEMINI_API_KEY`, regenerate a fresh `DJANGO_SECRET_KEY` on PythonAnywhere, and change the `admin` operator password (because legacy fallback secret `15aace6` and tracked `db.sqlite3` snapshots with the `admin` PBKDF2 hash remain in historical Git commits prior to untracking in `fbf94a4`, and `GEMINI_API_KEY` was shared externally in chat).
2. **Run Dedicated Offline Scanners on CI/Host:** `pip-audit` and `bandit` were not installed in this environment; secondary packages reported by `pip list --outdated` (such as `asgiref`, `cryptography`, `sqlparse`) should be periodically updated alongside `requirements.txt` pins.

---

## 2. Scope & Methodology

- **Static Code & Configuration Review:** Settings, WSGI (`pythonanywhere_wsgi.py`), middleware, URLs, forms, validators, models, views, management commands, templates, and vanilla JavaScript.
- **Dynamic Verification:** Django `TestCase` and `Client(enforce_csrf_checks=True)` testing across anonymous, non-staff authenticated, and staff operator contexts (`71` total automated tests).
- **Production Configuration Check:** `python manage.py check --deploy` under `DJANGO_DEBUG=False` and `python manage.py makemigrations --check --dry-run`.
- **Static Pattern Audit:** Repository-wide Python scan for dangerous sinks (`eval(`, `exec(`, `pickle.load`, `yaml.load(`, `os.system(`, `subprocess.`, `mark_safe(`, `.raw(`, `.extra(`, `cursor.execute`) and hardcoded key prefixes (`AIza`, `AQ.Ab8`).

---

## 3. OWASP Top 10 Findings & Remediations

### A01 — Broken Access Control
- **Bypassable `/sys-admin/login/` Route:** Raw Django Admin login exposed at `/sys-admin/login/` bypassed the custom CAPTCHA-protected operator login GUI.
  - **Fix (`config/urls.py`):** Routed `sys-admin/login/` and `sys-admin/logout/` cleanly through `portal_login_view` and `portal_logout_view` before `admin.site.urls`.
- **Unvalidated Open Redirects:** `portal_login_view` redirected to arbitrary `next` query/POST values, and `message_toggle_read_view` trusted arbitrary `HTTP_REFERER` headers.
  - **Fix (`portal/views.py`):** Added `_get_safe_redirect_url()` using `django.utils.http.url_has_allowed_host_and_scheme` restricted to `{request.get_host()}`.
- **GET-Based CSRF State Mutations:** Operator logout, message deletion, message read/unread toggling, AJAX `message_detail_view` read marking, and project/skill/certification/experience deletes accepted HTTP `GET` requests.
  - **Fix (`portal/views.py`, templates):** Enforced `@require_POST` on all mutating views; updated `message_detail_view` so `GET` is strictly read-only while `POST` marks read; replaced `<a href="...">` action links across `templates/base.html`, `templates/portal/base_portal.html`, `messages_list.html`, `projects_list.html`, `skills_list.html`, `certifications_list.html`, and `experience_list.html` with CSRF-protected `<form method="post">` buttons (`fetch` in `messages_list.html` sends `POST` + `X-CSRFToken`).
- **Path Traversal Risk on Resume Downloads:** `download_resume_view` used prefix matching rather than canonical path containment.
  - **Fix (`core/views.py`):** Enforced `os.path.realpath` and `os.path.commonpath([media_root, file_path]) == media_root`, logging anomalies and falling back safely without leaking host files.

### A02 — Cryptographic Failures & Sensitive Data Exposure
- **Hardcoded Fallback `SECRET_KEY` in Settings:** Removed the static literal fallback key from `config/settings.py`.
  - **Fix (`config/settings.py`, `.gitignore`):** Uses `DJANGO_SECRET_KEY` from environment when set, or generates/loads an ephemeral local key in gitignored `.django_secret_key`.
- **Sensitive Data in Browser/Proxy Caches:** Added `Cache-Control: no-store, no-cache, must-revalidate, private`, `Pragma: no-cache`, and `Expires: 0` in `core/middleware.py` for `/portal/`, `/admin/`, `/sys-admin/`, and `/nexus/api/` endpoints.
- **Secret Scrubbing in Security Logs:** `core/security.py` and `ai_services/gemini.py` scrub `AIza...` / `AQ....` credential patterns as `[REDACTED_KEY]` and strip `\r`, `\n`, and `\0` characters to prevent log injection.

### A03 — Injection, XSS & SSRF
- **Unescaped Inline JSON Script Blocks:** `templates/core/index.html` manually constructed `<script id="projects-json-data">` and `<script id="topics-json-data">` JSON blocks with `|escapejs`.
  - **Fix (`core/views.py`, `templates/core/index.html`):** Switched to Django's `{{ projects_json_map|json_script:"projects-json-data" }}` and `{{ topics_json_map|json_script:"topics-json-data" }}`.
- **DOM `innerHTML` Sink in Network Visualizer:** Replaced `tooltip.innerHTML = ...` in `static/js/network-viz.js` (synced via `collectstatic` to `staticfiles/js/network-viz.js`) with `document.createElement`, `textContent`, and `replaceChildren`.
- **Unsafe URI Schemes in Profile Links:** `SocialLink.url` used a plain `CharField` permitting `javascript:` or `data:` links.
  - **Fix (`core/validators.py`, `portfolio/models.py`):** Added `validate_safe_url` restricting values to `http://`, `https://`, or `mailto:` and rejecting control characters.
- **Unvalidated Gemini Model Path Interpolation (SSRF / Path Injection):** `GeminiClient` interpolated `preferred_model` into Google endpoint URLs without format validation.
  - **Fix (`ai_services/gemini.py`, `portal/forms.py`):** Enforced strict regex `r'^[a-zA-Z0-9._\-]{3,64}$'` prior to HTTP dispatch (`GEMINI_INVALID_MODEL`) and in `AISettingsForm.clean_preferred_model()`.
- **SQL / Execution Sink Check:** Repository scan found **0** usages of `.raw()`, `.extra()`, `cursor.execute`, `eval()`, runtime Python `exec()`, `pickle.load`, `yaml.load()`, `os.system()`, or `subprocess.` in application code.

### A04 & A07 — Insecure Design, Authentication & Abuse Prevention
- **Missing Login Brute-Force Protection & Predictable CAPTCHA RNG:** `portal_login_view` lacked failed-attempt throttling, CAPTCHA had no expiration, and `portal/captcha.py` used non-CSPRNG `random`.
  - **Fix (`portal/captcha.py`, `portal/models.py`, `portal/admin.py`, `portal/views.py`):** Switched CAPTCHA generation to `secrets` (CSPRNG, 6-char challenge); added 180-second fail-closed CAPTCHA expiration (`portal_captcha_ts`), session refresh rate limit (30/min), and `LoginAttemptLog` sliding-window IP throttling returning HTTP `429` after 5 failures in 15 minutes.
- **Spoofable `X-Forwarded-For` Client IP Headers:** `X-Forwarded-For` leftmost IP trust allowed trivial rate-limit and quota bypasses.
  - **Fix (`core/security.py`, `contact/views.py`, `nexus/views.py`, `intelligence/views.py`, `pythonanywhere_wsgi.py`):** Replaced ad-hoc IP lookup with `core.security.get_client_ip()`, ignoring `X-Forwarded-For` unless `TRUST_PROXY_HEADERS=True` (`DJANGO_TRUST_PROXY_HEADERS='True'` on PythonAnywhere WSGI), where it selects `HTTP_X_REAL_IP` or the rightmost proxy-appended IP.
- **Unbounded Search Input:** Capped `?q=` search queries in `portal/views.py` (`messages_list_view`) and `intelligence/views.py` (`[:120]`, `category` `[:80]`).

### A05 — Security Misconfiguration & Deployment Hardening
- **Reverse-Proxy SSL Redirect Loop Risk:** Added `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')` in `config/settings.py` (enabled with `DJANGO_BEHIND_HTTPS_PROXY='True'` in `pythonanywhere_wsgi.py`) so `SECURE_SSL_REDIRECT = True` functions cleanly behind PythonAnywhere's nginx TLS terminator.
- **Upload Limits, Session Lifetime & CSP:** Enforced `SESSION_COOKIE_AGE = 28800`, upload memory/request caps (`6 MB` / `5 MB`), added `object-src 'none'` to `Content-Security-Policy` in `core/middleware.py`, added `/robots.txt` blocking `/portal/`, `/admin/`, `/sys-admin/`, and configured rotating `logs/security.log` telemetry.

### A08 — File Upload & Subresource Integrity (SRI)
- **Unvalidated File Uploads:** Added `SafeUploadPath` (UUID hex filenames), `validate_image_file` (`.jpg/.jpeg/.png/.webp`, 5 MB cap, PIL `.verify()`, max `4096x4096` px, blocking SVGs), and `validate_resume_file` (5 MB cap, `%PDF-` header verify, DOCX ZIP structure `[Content_Types].xml` + `word/document.xml` + `<=25 MB` uncompressed cap) across `core.models`, `portfolio.models`, and `intelligence.models`.
- **CDN Integrity Pinning:** Added SHA-384 `integrity` hash (`sha384-XGjxtQfXaH2tnPFa9x+ruJTuLE3Aa6LhHSWRr1XeTyhezb4abCG4ccI5AkVDxqC+`) and `crossorigin="anonymous"` to Bootstrap Icons `1.11.3` stylesheet links in `templates/base.html`, `templates/portal/base_portal.html`, and `templates/portal/login.html`.

---

## 4. Dependency & Environment Audit

- **Upgraded Packages (`requirements.txt` & active environment):**
  - `Django` -> `6.1.3` (`>=6.1.3,<7.0` on Python >=3.12; `>=5.2.12,<6.0` on Python <3.12)
  - `pillow` -> `13.0.0` (`>=13.0.0; python_version >= "3.11"`, with Python 3.10 fallback `>=12.3.0,<13.0` in `requirements.txt`; upgrading PythonAnywhere's virtualenv from Python 3.10 to 3.11+ is recommended for Pillow 13.x & Django 6.1.x)
  - `python-dotenv` -> `1.2.4` (`>=1.2.4`)
  - `urllib3` -> `2.8.0` (`>=2.8.0`)
  - `certifi` -> `2026.11.20` (`>=2026.11.20`)
  - `requests` `2.34.2`, `whitenoise` `6.12.0`
- **Additional Outdated Packages Noted by `pip list --outdated`:** Secondary environment packages (`asgiref 3.12.1 -> 3.13.0`, `cryptography 50.0.0 -> 50.0.2`, `sqlparse 0.5.5 -> 0.6.1`, `gunicorn 26.0.0 -> 27.0.0`, etc.) remain upgradable outside minimal `requirements.txt` constraints.

---

## 5. Verification Matrix

| # | Security Area / Check | Verification Method & Evidence | Status |
|---|---|---|---|
| 1 | Broken Access Control (Anonymous & Non-Staff) | Verified `302` redirect to login and zero DB mutation across `/portal/*`, `/sys-admin/`, and admin POST endpoints in `core/security_tests.py` & `portal/tests.py` | **PASSED** |
| 2 | `/sys-admin/login/` & `/admin/login/` CAPTCHA Gate | Verified custom `OPERATOR ACCESS` GUI serves challenge and blocks missing/invalid CAPTCHA with `200` / no session created (`core/security_tests.py`) | **PASSED** |
| 3 | Cryptographic Secrets & Credential Exposure | Verified `.env`, `.django_secret_key`, `db.sqlite3`, and `logs/` are untracked; static scan clean. **Owner must still rotate `GEMINI_API_KEY`, historical `admin` password, and `DJANGO_SECRET_KEY`.** | **NEEDS REVIEW** |
| 4 | Injection, XSS (`json_script`, Tooltip DOM) & Safe URLs | Verified `</script><script>` escaping as `\u003C/script\u003E`, `validate_safe_url` rejection of `javascript:`/`data:`, safe `network-viz.js` DOM APIs, and 0 unsafe sinks in static scan | **PASSED** |
| 5 | CSRF & HTTP Method Enforcement (`@require_POST`) | Verified HTTP `405` on `GET` to logout, toggle-read, and all portal delete endpoints; `GET` read-only detail; HTTP `403` via `Client(enforce_csrf_checks=True)` | **PASSED** |
| 6 | Open Redirect Prevention | Verified malicious `next` (`https://evil.example`, `//evil.example`) and `HTTP_REFERER` fall back to safe internal routes via `url_has_allowed_host_and_scheme` | **PASSED** |
| 7 | Brute-Force Lockout & CAPTCHA Hardening | Verified CSPRNG CAPTCHA, 180s expiry failure, and HTTP `429` IP lockout after 5 failures via `LoginAttemptLog` (`core/security_tests.py`) | **PASSED** |
| 8 | Proxy & IP Spoofing Defense | Verified `get_client_ip` ignores spoofed `X-Forwarded-For` when `TRUST_PROXY_HEADERS=False` and extracts rightmost proxy hop when `True`; CRLF/secret scrubbing tested | **PASSED** |
| 9 | File Upload Validation & Resume Path Containment | Verified UUID filenames (`SafeUploadPath`), PIL raster checks / SVG rejection, `%PDF-` / DOCX archive validation, and `os.path.commonpath` traversal block | **PASSED** |
| 10 | Gemini AI SSRF / Model Validation & Rate Limiting | Verified regex model rejection prevents HTTP calls (`GEMINI_INVALID_MODEL`), server-side API key usage, secret log scrubbing, and chat throttling | **PASSED** |
| 11 | Security Headers & Cache Control | Verified live responses return `CSP` (`object-src 'none'`), `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Permissions-Policy`, and `Cache-Control: no-store` on `/portal/login/` & `/nexus/api/status/` | **PASSED** |
| 12 | Django Production Deployment Checks | `python manage.py check --deploy` (`DJANGO_DEBUG=False`) and `makemigrations --check --dry-run` both passed cleanly (`0` issues) | **PASSED** |
| 13 | Dependency & Automated Scanner Coverage | Core packages patched in `requirements.txt`, but `pip-audit` and `bandit` were not installed here and secondary packages remain behind latest versions in `pip list --outdated` | **NEEDS REVIEW** |
| 14 | Full Automated Test Suite | Executed `python manage.py test` after final edits: **71 tests ran in 37.740s — OK** (`0` failures, `0` errors, `0` skipped) | **PASSED** |

---

## 6. Post-Deployment Owner Checklist

1. **Rotate Credentials Immediately:**
   - Revoke and regenerate the Google `GEMINI_API_KEY` in Google AI Studio and update PythonAnywhere `.env` / WSGI environment variables.
   - Generate a new 50+ character `DJANGO_SECRET_KEY` on PythonAnywhere (do not reuse any prior key).
   - Run `python manage.py changepassword admin` on PythonAnywhere to rotate the operator password (since old Git commits contained historical `db.sqlite3` snapshots).
2. **Pull, Migrate & Reload on PythonAnywhere:**
   - `git pull origin main`
   - `pip install -r requirements.txt`
   - `python manage.py migrate`
   - `python manage.py collectstatic --noinput`
   - Reload web app in the PythonAnywhere **Web** tab.
