/**
 * ramo.ai — Networking & Cybersecurity Assistant Client Engine
 * Security-hardened: No API keys in JS, strict DOM rendering (zero raw innerHTML),
 * CSRF-protected POST requests, sessionStorage history with clear/new chat actions.
 */
(function () {
  const launcher = document.getElementById('nexus-launcher-btn');
  const navBtn = document.getElementById('nav-nexus-btn');
  const panel = document.getElementById('nexus-chat-panel');
  const closeBtn = document.getElementById('nexus-close-btn');
  const newChatBtn = document.getElementById('nexus-new-chat-btn');
  const clearBtn = document.getElementById('nexus-clear-btn');
  const messagesEl = document.getElementById('nexus-messages-body');
  const form = document.getElementById('nexus-chat-form');
  const inputEl = document.getElementById('nexus-input');
  const sendBtn = document.getElementById('nexus-send-btn');
  const quotaEl = document.getElementById('nexus-quota-pill');

  if (!launcher || !panel || !messagesEl || !form || !inputEl) return;

  const STORAGE_KEY = 'nexus_chat_history_v1';
  const MAX_STORED_TURNS = 16;
  const CHAT_ENDPOINT = panel.getAttribute('data-chat-url') || '/nexus/api/chat/';
  const STATUS_ENDPOINT = panel.getAttribute('data-status-url') || '/nexus/api/status/';
  const IS_AVAILABLE = panel.getAttribute('data-available') === 'true';

  let conversationHistory = [];
  let isSending = false;

  const SUGGESTED_PROMPTS = [
    'Explain VLANs with a practical example.',
    'How does a firewall inspect network traffic?',
    'Teach me subnetting.',
    'Explain SQL injection and its prevention.',
    'How does Active Directory work?',
    "Tell me about Abhiram's projects."
  ];

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }

  function scrollToLatest() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function openPanel() {
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    inputEl.focus();
    scrollToLatest();
  }

  function closePanel() {
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
  }

  function togglePanel() {
    if (panel.classList.contains('open')) {
      closePanel();
    } else {
      openPanel();
    }
  }

  /**
   * Safe inline text formatting parser (bold + inline code) using DOM text nodes only.
   */
  function appendInlineFormatted(parent, text) {
    const tokenRegex = /(`[^`]+`|\*\*[^*]+\*\*)/g;
    let lastIndex = 0;
    let match;

    while ((match = tokenRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parent.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
      }
      const token = match[0];
      if (token.startsWith('`') && token.endsWith('`')) {
        const code = document.createElement('code');
        code.className = 'nexus-inline-code';
        code.textContent = token.slice(1, -1);
        parent.appendChild(code);
      } else if (token.startsWith('**') && token.endsWith('**')) {
        const strong = document.createElement('strong');
        strong.textContent = token.slice(2, -2);
        parent.appendChild(strong);
      }
      lastIndex = tokenRegex.lastIndex;
    }

    if (lastIndex < text.length) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex)));
    }
  }

  /**
   * Renders assistant Markdown safely into DOM elements (zero innerHTML execution).
   */
  function renderSafeMarkdown(container, rawText) {
    const segments = rawText.split(/(```[\s\S]*?```)/g);

    segments.forEach(segment => {
      if (!segment) return;

      if (segment.startsWith('```') && segment.endsWith('```')) {
        const lines = segment.slice(3, -3).split('\n');
        let lang = 'code';
        if (lines.length > 1 && /^[a-zA-Z0-9_+-]{1,20}$/.test(lines[0].trim())) {
          lang = lines.shift().trim();
        }
        const codeBody = lines.join('\n').replace(/^\n+|\n+$/g, '');

        const block = document.createElement('div');
        block.className = 'nexus-code-block';

        const header = document.createElement('div');
        header.className = 'nexus-code-header';

        const langSpan = document.createElement('span');
        langSpan.textContent = lang.toUpperCase();

        const copyBtn = document.createElement('button');
        copyBtn.type = 'button';
        copyBtn.className = 'nexus-code-copy-btn';
        copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy Code';
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(codeBody).then(() => {
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
              copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy Code';
            }, 1400);
          }).catch(() => {});
        });

        header.appendChild(langSpan);
        header.appendChild(copyBtn);

        const pre = document.createElement('pre');
        pre.className = 'nexus-code-pre';
        const codeEl = document.createElement('code');
        codeEl.textContent = codeBody;
        pre.appendChild(codeEl);

        block.appendChild(header);
        block.appendChild(pre);
        container.appendChild(block);
        return;
      }

      // Plain text / headings / lists
      const lines = segment.split('\n');
      let currentList = null;

      lines.forEach(line => {
        const trimmed = line.trim();
        if (!trimmed) {
          currentList = null;
          return;
        }

        if (/^#{1,4}\s+/.test(trimmed)) {
          currentList = null;
          const h = document.createElement('div');
          h.className = 'nexus-md-h';
          appendInlineFormatted(h, trimmed.replace(/^#{1,4}\s+/, ''));
          container.appendChild(h);
        } else if (/^[-*•]\s+/.test(trimmed) || /^\d+\.\s+/.test(trimmed)) {
          if (!currentList) {
            currentList = document.createElement(trimmed[0] >= '0' && trimmed[0] <= '9' ? 'ol' : 'ul');
            currentList.className = 'nexus-md-list';
            container.appendChild(currentList);
          }
          const li = document.createElement('li');
          appendInlineFormatted(li, trimmed.replace(/^([-*•]|\d+\.)\s+/, ''));
          currentList.appendChild(li);
        } else {
          currentList = null;
          const p = document.createElement('p');
          p.className = 'nexus-md-p';
          appendInlineFormatted(p, trimmed);
          container.appendChild(p);
        }
      });
    });
  }

  function appendMessageBubble(role, text, isError = false) {
    const row = document.createElement('div');
    row.className = `nexus-msg-row ${role === 'user' ? 'user' : 'assistant'}`;

    const meta = document.createElement('div');
    meta.className = 'nexus-msg-meta';
    meta.textContent = role === 'user' ? 'YOU' : 'ramo.ai';
    row.appendChild(meta);

    const bubble = document.createElement('div');
    bubble.className = `nexus-bubble${isError ? ' error-bubble' : ''}`;

    if (role === 'user' || isError) {
      bubble.textContent = text;
    } else {
      renderSafeMarkdown(bubble, text);
    }
    row.appendChild(bubble);

    if (role === 'model' && !isError) {
      const footerActions = document.createElement('div');
      footerActions.className = 'nexus-msg-footer-actions';

      const copyRespBtn = document.createElement('button');
      copyRespBtn.type = 'button';
      copyRespBtn.className = 'nexus-copy-resp-btn';
      copyRespBtn.innerHTML = '<i class="bi bi-copy"></i> Copy response';
      copyRespBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(text).then(() => {
          copyRespBtn.textContent = 'Copied!';
          setTimeout(() => {
            copyRespBtn.innerHTML = '<i class="bi bi-copy"></i> Copy response';
          }, 1400);
        }).catch(() => {});
      });

      footerActions.appendChild(copyRespBtn);
      row.appendChild(footerActions);
    }

    messagesEl.appendChild(row);
    scrollToLatest();
  }

  function renderWelcomeState() {
    while (messagesEl.firstChild) {
      messagesEl.removeChild(messagesEl.firstChild);
    }

    const introText = IS_AVAILABLE
      ? "Hello! I'm **ramo.ai**, Abhiram Anil's networking & cybersecurity assistant.\n\nAsk me anything about **OSI/TCP-IP, subnetting, VLANs, firewalls, Nmap/Wireshark/Burp Suite, Active Directory, Django security**, or **Abhiram's verified background and projects**."
      : "ramo.ai is currently **offline** because server API credentials are not configured or chat has been paused by the administrator. All portfolio tools, Subnet Calculator, and Topology Simulators remain fully functional.";

    appendMessageBubble('model', introText);

    if (IS_AVAILABLE) {
      const wrap = document.createElement('div');
      wrap.className = 'nexus-suggestions-wrap';
      wrap.id = 'nexus-suggestions-wrap';

      SUGGESTED_PROMPTS.forEach(promptText => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'nexus-suggestion-chip';
        chip.textContent = promptText;
        chip.addEventListener('click', () => {
          inputEl.value = promptText;
          submitQuestion(promptText);
        });
        wrap.appendChild(chip);
      });

      messagesEl.appendChild(wrap);
    }
    scrollToLatest();
  }

  function showTypingIndicator() {
    removeTypingIndicator();
    const row = document.createElement('div');
    row.className = 'nexus-msg-row assistant';
    row.id = 'nexus-typing-row';

    const indicator = document.createElement('div');
    indicator.className = 'nexus-typing-indicator';
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('span');
      dot.className = 'nexus-typing-dot';
      indicator.appendChild(dot);
    }
    row.appendChild(indicator);
    messagesEl.appendChild(row);
    scrollToLatest();
  }

  function removeTypingIndicator() {
    const existing = document.getElementById('nexus-typing-row');
    if (existing) existing.remove();
  }

  function saveHistoryToSession() {
    try {
      const trimmed = conversationHistory.slice(-MAX_STORED_TURNS);
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
    } catch (_) {}
  }

  function loadHistoryFromSession() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        conversationHistory = parsed.filter(
          item => item && (item.role === 'user' || item.role === 'model') && typeof item.content === 'string'
        ).slice(-MAX_STORED_TURNS);
      }
    } catch (_) {
      conversationHistory = [];
    }
  }

  function resetConversation() {
    conversationHistory = [];
    try { sessionStorage.removeItem(STORAGE_KEY); } catch (_) {}
    renderWelcomeState();
  }

  async function submitQuestion(text) {
    const message = (text || '').trim();
    if (!message || isSending) return;

    const suggestions = document.getElementById('nexus-suggestions-wrap');
    if (suggestions) suggestions.remove();

    isSending = true;
    sendBtn.disabled = true;
    inputEl.value = '';
    inputEl.style.height = 'auto';

    appendMessageBubble('user', message);
    showTypingIndicator();

    const historyToSend = conversationHistory.slice(-10);

    try {
      const resp = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: JSON.stringify({
          message: message,
          history: historyToSend,
        }),
      });

      const data = await resp.json();
      removeTypingIndicator();

      if (resp.ok && data.status === 'ok') {
        appendMessageBubble('model', data.reply);
        conversationHistory.push({ role: 'user', content: message });
        conversationHistory.push({ role: 'model', content: data.reply });
        saveHistoryToSession();

        if (quotaEl && typeof data.remaining_today === 'number') {
          quotaEl.textContent = `${data.remaining_today} queries left today`;
        }
      } else {
        appendMessageBubble('model', data.message || 'Unable to reach ramo.ai right now.', true);
        if (quotaEl && typeof data.remaining_today === 'number') {
          quotaEl.textContent = `${data.remaining_today} queries left today`;
        }
      }
    } catch (err) {
      removeTypingIndicator();
      appendMessageBubble('model', 'Network interruption occurred while contacting ramo.ai. Please retry shortly.', true);
    } finally {
      isSending = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }
  }

  // Event Bindings
  launcher.addEventListener('click', togglePanel);
  if (navBtn) navBtn.addEventListener('click', togglePanel);
  document.querySelectorAll('[data-open-ramo-ai]').forEach(btn => {
    btn.addEventListener('click', openPanel);
  });
  if (closeBtn) closeBtn.addEventListener('click', closePanel);
  if (newChatBtn) newChatBtn.addEventListener('click', resetConversation);
  if (clearBtn) clearBtn.addEventListener('click', resetConversation);

  form.addEventListener('submit', e => {
    e.preventDefault();
    submitQuestion(inputEl.value);
  });

  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submitQuestion(inputEl.value);
    }
  });

  inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 96) + 'px';
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && panel.classList.contains('open')) {
      closePanel();
    }
  });

  // Restore conversation or initialize welcome
  loadHistoryFromSession();
  if (conversationHistory.length > 0 && IS_AVAILABLE) {
    while (messagesEl.firstChild) messagesEl.removeChild(messagesEl.firstChild);
    conversationHistory.forEach(item => appendMessageBubble(item.role, item.content));
  } else {
    renderWelcomeState();
  }

  // Refresh live quota indicator silently
  if (IS_AVAILABLE) {
    fetch(STATUS_ENDPOINT)
      .then(r => r.json())
      .then(data => {
        if (quotaEl && typeof data.remaining_today === 'number') {
          quotaEl.textContent = `${data.remaining_today}/${data.daily_limit} left today`;
        }
      })
      .catch(() => {});
  }
})();
