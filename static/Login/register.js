/* ===================================================
   PHISHGUARD — register.js
   Handles: Register / Create Account page only
   Features: Real-time codename check + suggestions
   =================================================== */
(function () {
  'use strict';

  /* ── Field error helpers ──────────────────────── */
  function setErr(inputId, errId, msg) {
    var inp = document.getElementById(inputId);
    var err = document.getElementById(errId);
    if (!inp || !err) return;
    if (msg) {
      inp.classList.add('pg-input--error');
      err.textContent = '⚡ ' + msg;
    } else {
      inp.classList.remove('pg-input--error');
      err.textContent = '';
    }
  }

  function clearAll() {
    ['new_agent','new_email','new_code','confirm_code'].forEach(function (id) {
      var inp = document.getElementById(id);
      if (inp) inp.classList.remove('pg-input--error');
    });
    ['err_new_agent','err_new_email','err_new_code','err_confirm_code'].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.textContent = '';
    });
  }

  /* ── Eye toggles ──────────────────────────────── */
  function bindEye(btnId, inputId) {
    var btn = document.getElementById(btnId);
    var inp = document.getElementById(inputId);
    if (!btn || !inp) return;
    btn.addEventListener('click', function () {
      var show = inp.type === 'password';
      inp.type = show ? 'text' : 'password';
      btn.style.color = show ? 'var(--pg-green)' : 'var(--pg-text-dim)';
    });
  }

  bindEye('toggleNewPw',     'new_code');
  bindEye('toggleConfirmPw', 'confirm_code');

  /* ── Password strength meter ──────────────────── */
  var codeInput = document.getElementById('new_code');
  if (codeInput) {
    codeInput.addEventListener('input', function () {
      var val   = this.value;
      var fill  = document.getElementById('strengthFill');
      var label = document.getElementById('strengthText');
      var score = 0;

      if (val.length >= 8)           score++;
      if (/[A-Z]/.test(val))         score++;
      if (/[0-9]/.test(val))         score++;
      if (/[^a-zA-Z0-9]/.test(val))  score++;

      var levels = [
        { pct: 0,   color: '#ff3b3b', text: '—'        },
        { pct: 25,  color: '#ff3b3b', text: 'WEAK'      },
        { pct: 50,  color: '#ffaa00', text: 'MODERATE'  },
        { pct: 75,  color: '#00ccff', text: 'STRONG'    },
        { pct: 100, color: '#00ff41', text: 'MAXIMUM'   },
      ];

      var lvl = (val.length === 0) ? levels[0] : levels[score];
      if (fill)  { fill.style.width = lvl.pct + '%'; fill.style.background = lvl.color; }
      if (label) { label.textContent = lvl.text; label.style.color = lvl.color; }
    });
  }

  /* ── Real-time codename availability check ────── */
  var codenameInput   = document.getElementById('new_agent');
  var codenameErr     = document.getElementById('err_new_agent');
  var suggestionsBox  = document.getElementById('codename_suggestions');
  var checkTimer      = null;

  function showSuggestions(suggestions) {
    if (!suggestionsBox) return;
    if (!suggestions || suggestions.length === 0) {
      suggestionsBox.innerHTML = '';
      suggestionsBox.style.display = 'none';
      return;
    }

    var html = '<span class="pg-suggest-label">AVAILABLE CODENAMES:</span>';
    suggestions.forEach(function (name) {
      html += '<button type="button" class="pg-suggest-btn" data-name="' + name + '">' + name + '</button>';
    });

    suggestionsBox.innerHTML = html;
    suggestionsBox.style.display = 'block';

    // Click suggestion → fill in the input
    suggestionsBox.querySelectorAll('.pg-suggest-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        codenameInput.value = this.getAttribute('data-name');
        codenameInput.classList.remove('pg-input--error');
        codenameInput.classList.add('pg-input--available');
        if (codenameErr) codenameErr.textContent = '✔ Codename is available!';
        codenameErr.style.color = 'var(--pg-green)';
        suggestionsBox.style.display = 'none';
      });
    });
  }

  function checkCodename(codename) {
    if (!codename || codename.length < 3) {
      showSuggestions([]);
      return;
    }

    fetch('/check-codename/?codename=' + encodeURIComponent(codename))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (!codenameErr) return;

        if (data.available) {
          // ✔ Available
          codenameInput.classList.remove('pg-input--error');
          codenameInput.classList.add('pg-input--available');
          codenameErr.textContent = '✔ Codename is available!';
          codenameErr.style.color = 'var(--pg-green)';
          showSuggestions([]);
        } else {
          // ✗ Taken — show suggestions
          codenameInput.classList.add('pg-input--error');
          codenameInput.classList.remove('pg-input--available');
          codenameErr.textContent = '⚡ Codename already taken. Try one below:';
          codenameErr.style.color = 'var(--pg-red)';
          showSuggestions(data.suggestions);
        }
      })
      .catch(function () {
        // Silently fail — server-side will catch it on submit
      });
  }

  if (codenameInput) {
    codenameInput.addEventListener('input', function () {
      var val = this.value.trim();

      // Clear previous state
      codenameInput.classList.remove('pg-input--available');
      if (codenameErr) {
        codenameErr.textContent = '';
        codenameErr.style.color = '';
      }
      showSuggestions([]);

      // Debounce — wait 500ms after user stops typing
      clearTimeout(checkTimer);
      if (val.length >= 3) {
        codenameErr.textContent = 'CHECKING...';
        codenameErr.style.color = 'var(--pg-text-dim)';
        checkTimer = setTimeout(function () {
          checkCodename(val);
        }, 500);
      }
    });
  }



  /* ── Real-time email MX check ────────────────── */
  var emailInput  = document.getElementById('new_email');
  var emailErr    = document.getElementById('err_new_email');
  var emailTimer  = null;

  if (emailInput) {
    emailInput.addEventListener('input', function () {
      var val = this.value.trim();

      // Clear previous state
      emailInput.classList.remove('pg-input--available', 'pg-input--error');
      if (emailErr) { emailErr.textContent = ''; emailErr.style.color = ''; }

      // Only check if looks like full email
      if (val.indexOf('@') === -1 || val.split('@')[1] === '') return;

      clearTimeout(emailTimer);
      emailErr.textContent = 'CHECKING DOMAIN...';
      emailErr.style.color = 'var(--pg-text-dim)';

      emailTimer = setTimeout(function () {
        fetch('/check-email-mx/?email=' + encodeURIComponent(val))
          .then(function (res) { return res.json(); })
          .then(function (data) {
            if (!emailErr) return;
            if (data.valid) {
              emailInput.classList.remove('pg-input--error');
              emailInput.classList.add('pg-input--available');
              emailErr.textContent = data.message;
              emailErr.style.color = 'var(--pg-green)';
            } else {
              emailInput.classList.add('pg-input--error');
              emailInput.classList.remove('pg-input--available');
              emailErr.textContent = '⚡ ' + data.message;
              emailErr.style.color = 'var(--pg-red)';
            }
          })
          .catch(function () {
            // Silently fail — server-side will catch on submit
            if (emailErr) emailErr.textContent = '';
          });
      }, 700); // wait 700ms after user stops typing
    });
  }

  /* ── Terms of Service Modal ───────────────────── */
  var tosOverlay  = document.getElementById('tosOverlay');
  var openTosBtn  = document.getElementById('openTos');
  var tosAccept   = document.getElementById('tosAccept');
  var tosDecline  = document.getElementById('tosDecline');
  var termsCheck  = document.getElementById('termsCheck');
  var errTerms    = document.getElementById('err_terms');

  // Open modal
  if (openTosBtn) {
    openTosBtn.addEventListener('click', function () {
      tosOverlay.classList.add('active');
      // Scroll modal body to top
      var body = tosOverlay.querySelector('.tos-body');
      if (body) body.scrollTop = 0;
    });
  }

  // Accept — check the checkbox and close
  if (tosAccept) {
    tosAccept.addEventListener('click', function () {
      if (termsCheck) termsCheck.checked = true;
      if (errTerms)   { errTerms.textContent = ''; }
      tosOverlay.classList.remove('active');
    });
  }

  // Decline — uncheck and close
  if (tosDecline) {
    tosDecline.addEventListener('click', function () {
      if (termsCheck) termsCheck.checked = false;
      tosOverlay.classList.remove('active');
    });
  }

  // X button — close without accepting
  var tosClose = document.getElementById('tosClose');
  if (tosClose) {
    tosClose.addEventListener('click', function () {
      tosOverlay.classList.remove('active');
    });
  }

  // Click outside modal to close
  if (tosOverlay) {
    tosOverlay.addEventListener('click', function (e) {
      if (e.target === tosOverlay) {
        tosOverlay.classList.remove('active');
      }
    });
  }


  /* ── Real-time email typo detection ──────────── */
  var emailInput  = document.getElementById('new_email');
  var emailErr    = document.getElementById('err_new_email');

  // Same typo map as server-side
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

  function checkEmailTypo(email) {
    var parts = email.split('@');
    if (parts.length !== 2) return null;
    var domain = parts[1].toLowerCase();
    if (EMAIL_TYPO_MAP[domain]) {
      return parts[0] + '@' + EMAIL_TYPO_MAP[domain];
    }
    return null;
  }

  function validateEmailFormat(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  if (emailInput) {
    emailInput.addEventListener('input', function () {
      var val = this.value.trim();

      // Clear previous state
      emailInput.classList.remove('pg-input--error', 'pg-input--available');
      if (emailErr) {
        emailErr.textContent = '';
        emailErr.style.color = '';
      }

      if (!val) return;

      // Check for typo first
      var suggestion = checkEmailTypo(val);
      if (suggestion) {
        emailInput.classList.add('pg-input--error');
        if (emailErr) {
          emailErr.style.color = 'var(--pg-cyan)';
          emailErr.innerHTML = '⚡ Did you mean <strong style="color:var(--pg-green);cursor:pointer;" id="emailSuggest">' + suggestion + '</strong>? <span style="color:var(--pg-text-dim);font-size:.6rem;">(click to fix)</span>';

          // Click suggestion to auto-fix
          setTimeout(function() {
            var suggestEl = document.getElementById('emailSuggest');
            if (suggestEl) {
              suggestEl.addEventListener('click', function () {
                emailInput.value = suggestion;
                emailInput.classList.remove('pg-input--error');
                emailInput.classList.add('pg-input--available');
                if (emailErr) {
                  emailErr.textContent = '✔ Email looks good!';
                  emailErr.style.color = 'var(--pg-green)';
                }
              });
            }
          }, 50);
        }
        return;
      }

      // Check format validity
      if (val.includes('@')) {
        if (validateEmailFormat(val)) {
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

  /* ── Form validation before submit ───────────── */
  var form = document.getElementById('createForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      clearAll();

      var agent   = document.getElementById('new_agent').value.trim();
      var email   = document.getElementById('new_email').value.trim();
      var code    = document.getElementById('new_code').value;
      var confirm = document.getElementById('confirm_code').value;
      var ok      = true;

      if (!agent) {
        setErr('new_agent', 'err_new_agent', 'Codename is required.');
        ok = false;
      } else if (agent.length < 3) {
        setErr('new_agent', 'err_new_agent', 'Codename must be at least 3 characters.');
        ok = false;
      }

      if (!email) {
        setErr('new_email', 'err_new_email', 'Email is required.');
        ok = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setErr('new_email', 'err_new_email', 'Enter a valid email address.');
        ok = false;
      }

      if (!code) {
        setErr('new_code', 'err_new_code', 'Security code is required.');
        ok = false;
      } else if (code.length < 8) {
        setErr('new_code', 'err_new_code', 'Minimum 8 characters required.');
        ok = false;
      }

      if (!confirm) {
        setErr('confirm_code', 'err_confirm_code', 'Please confirm your code.');
        ok = false;
      } else if (code && confirm !== code) {
        setErr('confirm_code', 'err_confirm_code', 'Codes do not match.');
        ok = false;
      }

      // Terms checkbox validation
      var terms = document.getElementById('termsCheck');
      var errT  = document.getElementById('err_terms');
      if (terms && !terms.checked) {
        if (errT) {
          errT.textContent = '⚡ You must accept the Terms of Operation.';
          errT.style.color = 'var(--pg-red)';
        }
        ok = false;
      }

      if (!ok) e.preventDefault();
    });
  }

})();