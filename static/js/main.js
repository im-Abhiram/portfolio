/**
 * Main Application Script for Abhiram Anil Portfolio
 * Handles Navigation, Theme Toggling, Loading Screen, Modals, and AJAX Form
 */

document.addEventListener('DOMContentLoaded', () => {
  initLoadingScreen();
  initThemeToggle();
  initScrollProgress();
  initNavbarScroll();
  initSectionObserver();
  initBackToTop();
  initMobileNav();
  initClipboardCopy();
  initContactForm();
  initModalHandlers();
});

// 1. Loading Screen
function initLoadingScreen() {
  const loader = document.getElementById('loading-screen');
  const skipBtn = document.getElementById('loader-skip-btn');

  function dismissLoader() {
    if (loader && !loader.classList.contains('fade-out')) {
      loader.classList.add('fade-out');
      setTimeout(() => {
        loader.style.display = 'none';
      }, 450);
    }
  }

  // Dismiss when window loads or after max 1.2s timeout
  window.addEventListener('load', () => setTimeout(dismissLoader, 300));
  setTimeout(dismissLoader, 1200);

  if (skipBtn) {
    skipBtn.addEventListener('click', dismissLoader);
  }
}

// 2. Theme Toggle (Dark Default / High-Contrast Light)
function initThemeToggle() {
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const themeIcon = document.getElementById('theme-icon');
  
  // Read stored preference, default to 'dark'
  const currentTheme = localStorage.getItem('portfolio-theme') || 'dark';
  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
      localStorage.setItem('portfolio-theme', newTheme);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    if (themeIcon) {
      if (theme === 'light') {
        themeIcon.className = 'bi bi-moon-stars-fill';
        themeToggleBtn?.setAttribute('title', 'Switch to Dark NOC Mode');
      } else {
        themeIcon.className = 'bi bi-sun-fill';
        themeToggleBtn?.setAttribute('title', 'Switch to Day Mode');
      }
    }
  }
}

// 3. Scroll Progress Indicator
function initScrollProgress() {
  const progressBar = document.getElementById('scroll-progress');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight > 0) {
      const progressPercent = (window.scrollY / totalHeight) * 100;
      progressBar.style.width = `${progressPercent}%`;
    }
  }, { passive: true });
}

// 4. Sticky Navbar Scroll State
function initNavbarScroll() {
  const navbar = document.querySelector('.noc-navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, { passive: true });
}

// 5. Active Section Navigation Observer
function initSectionObserver() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link-item');
  if (!sections.length || !navLinks.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach(link => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, { threshold: 0.25 });

  sections.forEach(section => observer.observe(section));
}

// 6. Back to Top Button
function initBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// 7. Mobile Navigation Toggle
function initMobileNav() {
  const toggleBtn = document.querySelector('.mobile-menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (!toggleBtn || !navLinks) return;

  toggleBtn.addEventListener('click', () => {
    navLinks.classList.toggle('mobile-open');
    const isOpen = navLinks.classList.contains('mobile-open');
    toggleBtn.setAttribute('aria-expanded', isOpen);
  });

  // Close on nav link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('mobile-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
    });
  });
}

// 8. Copy to Clipboard Utility
function initClipboardCopy() {
  document.querySelectorAll('[data-copy]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const text = el.getAttribute('data-copy');
      if (!text) return;

      navigator.clipboard.writeText(text).then(() => {
        const originalHtml = el.innerHTML;
        el.innerHTML = '<i class="bi bi-check2"></i> Copied!';
        el.classList.add('copied');
        setTimeout(() => {
          el.innerHTML = originalHtml;
          el.classList.remove('copied');
        }, 2000);
      }).catch(err => {
        console.warn('Clipboard write failed:', err);
      });
    });
  });
}

// 9. Contact Form AJAX Submission with CSRF & Sanitization
function initContactForm() {
  const form = document.getElementById('contact-form');
  const alertContainer = document.getElementById('contact-alert-container');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Show loading state on button
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Transmitting...';
    
    // Clear previous alerts
    if (alertContainer) alertContainer.innerHTML = '';

    const formData = new FormData(form);
    formData.append('is_ajax', '1');

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        showAlert('success', data.message || 'Payload received successfully!');
        form.reset();
      } else {
        showAlert('error', data.message || 'Transmission error. Please verify input fields.');
      }
    } catch (err) {
      showAlert('error', 'Network transmission error. Check connection or try again.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
    }
  });

  function showAlert(type, text) {
    if (!alertContainer) return;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-box alert-${type}`;
    const iconClass = type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill';
    
    const icon = document.createElement('i');
    icon.className = `bi ${iconClass}`;
    
    const msg = document.createElement('span');
    msg.textContent = ' ' + text;
    
    alertDiv.appendChild(icon);
    alertDiv.appendChild(msg);
    alertContainer.appendChild(alertDiv);
  }
}

// 10. Generic Modals Controller
function initModalHandlers() {
  // Close modals on clicking backdrop or close button
  document.querySelectorAll('.noc-modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('open');
      }
    });
  });

  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const backdrop = btn.closest('.noc-modal-backdrop') || btn.closest('.terminal-modal-backdrop');
      if (backdrop) backdrop.classList.remove('open');
    });
  });

  // ESC key listener
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.noc-modal-backdrop.open, .terminal-modal-backdrop.open').forEach(modal => {
        modal.classList.remove('open');
      });
    }
  });

  // Security Concepts Accordion
  document.querySelectorAll('.concept-header').forEach(header => {
    header.addEventListener('click', () => {
      const parent = header.closest('.concept-item');
      if (parent) {
        parent.classList.toggle('open');
      }
    });
  });
}
