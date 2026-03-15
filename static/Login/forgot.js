/* ===================================================
   PHISHGUARD — forgot.js
   Handles: Forgot Password page only
   Features: Real-time email typo detection
   =================================================== */
(function () {
  'use strict';

  var emailInput = document.getElementById('forgot_email');
  var emailErr   = document.getElementById('err_forgot_email');

  /* ── Typo map ─────────────────────────────────── */
  var EMAIL_TYPO_MAP = {
    'gmil.com':     'gmail.com',
    'gmal.com':     'gmail.com',
    'gmai.com':     'gmail.com',
    'gamil.com':    'gmail.com',
    'gmail.con':    'gmail.com',
    'gmail.cpm':    'gmail.com',
    'gmail.ocm':    'gmail.com',
    'yaho.com':     'yahoo.com',
    'yahooo.com':   'yahoo.com',
    'yahoo.con':    'yahoo.com',
    'ymail.con':    'ymail.com',
    'hotmial.com':  'hotmail.com',
    'hotmail.con':  'hotmail.com',
    'outllook.com': 'outlook.com',
    'outlok.com':   'outlook.com',
    'outlook.con':  'outlook.com',
    'iclod.com':    'icloud.com',
    'icoud.com':    'icloud.com',
  };

  function checkTypo(email) {
    var parts = email.split('@');
    if (parts.length !== 2) return null;
    var domain = parts[1].toLowerCase();
    return EMAIL_TYPO_MAP[domain] ? parts[0] + '@' + EMAIL_TYPO_MAP[domain] : null;
  }

  function isValidFormat(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  /* ── Real-time validation ─────────────────────── */
  if (emailInput) {
    emailInput.addEventListener('input', function () {
      var val = this.value.trim();

      emailInput.classList.remove('pg-input--error', 'pg-input--available');
      if (emailErr) {
        emailErr.textContent = '';
        emailErr.style.color = '';
      }

      if (!val) return;

      // Typo check
      var suggestion = checkTypo(val);
      if (suggestion) {
        emailInput.classList.add('pg-input--error');
        if (emailErr) {
          emailErr.style.color = 'var(--pg-cyan)';
          emailErr.innerHTML = '⚡ Did you mean <strong style="color:var(--pg-green);cursor:pointer;" id="emailSuggest">'
            + suggestion
            + '</strong>? <span style="color:var(--pg-text-dim);font-size:.6rem;">(click to fix)</span>';

          setTimeout(function () {
            var el = document.getElementById('emailSuggest');
            if (el) {
              el.addEventListener('click', function () {
                emailInput.value = suggestion;
                emailInput.classList.remove('pg-input--error');
                emailInput.classList.add('pg-input--available');
                emailErr.textContent = '✔ Email looks good!';
                emailErr.style.color = 'var(--pg-green)';
              });
            }
          }, 50);
        }
        return;
      }

      // Format check
      if (val.includes('@')) {
        if (isValidFormat(val)) {
          emailInput.classList.add('pg-input--available');
          if (emailErr) {
            emailErr.textContent = '✔ Email format looks good!';
            emailErr.style.color = 'var(--pg-green)';
          }
        } else {
          emailInput.classList.add('pg-input--error');
          if (emailErr) {
            emailErr.textContent = '⚡ Enter a valid email (e.g. agent@gmail.com)';
            emailErr.style.color = 'var(--pg-red)';
          }
        }
      }
    });
  }

  /* ── Form submit validation ───────────────────── */
  var form = document.getElementById('forgotForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      var val = emailInput ? emailInput.value.trim() : '';

      if (emailInput) emailInput.classList.remove('pg-input--error');
      if (emailErr)   { emailErr.textContent = ''; emailErr.style.color = ''; }

      if (!val) {
        if (emailInput) emailInput.classList.add('pg-input--error');
        if (emailErr) {
          emailErr.textContent = '⚡ Email address is required.';
          emailErr.style.color = 'var(--pg-red)';
        }
        e.preventDefault();
        return;
      }

      if (!isValidFormat(val)) {
        if (emailInput) emailInput.classList.add('pg-input--error');
        if (emailErr) {
          emailErr.textContent = '⚡ Enter a valid email address.';
          emailErr.style.color = 'var(--pg-red)';
        }
        e.preventDefault();
      }
    });
  }

})();