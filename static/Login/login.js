/* ===================================================
   PHISHGUARD — login.js
   =================================================== */
(function () {
  'use strict';

  /* ── Eye toggle ──────────────────────────────── */
  var btn = document.getElementById('togglePw');
  var inp = document.getElementById('id_password');
  if (btn && inp) {
    btn.addEventListener('click', function () {
      var show = inp.type === 'password';
      inp.type = show ? 'text' : 'password';
      btn.style.color = show ? 'var(--pg-green)' : 'var(--pg-text-dim)';
    });
  }

  /* ── Client-side validation before submit ────── */
  var form = document.querySelector('.pg-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      var username = document.getElementById('id_username');
      var password = document.getElementById('id_password');
      var errU     = document.getElementById('err_username');
      var errP     = document.getElementById('err_password');
      var ok       = true;

      // Clear previous errors
      [username, password].forEach(function (el) {
        el.classList.remove('pg-input--error');
      });
      if (errU) errU.textContent = '';
      if (errP) errP.textContent = '';

      if (!username.value.trim()) {
        username.classList.add('pg-input--error');
        if (errU) errU.textContent = '⚡ Agent name is required.';
        ok = false;
      }

      if (!password.value) {
        password.classList.add('pg-input--error');
        if (errP) errP.textContent = '⚡ Security code is required.';
        ok = false;
      }

      if (!ok) e.preventDefault();
    });
  }

})();