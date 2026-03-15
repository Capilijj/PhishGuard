# =============================================================
#  emails.py
#  All outgoing email logic for PhishGuard.
#  views.py should call these functions — never send_mail() directly.
# =============================================================

from django.core.mail import send_mail
from django.conf import settings


# ── Verification email ────────────────────────────────────────

def send_verification_email(request, user_email, username, token):
    """
    Send an account verification link to the newly registered agent.
    Link: /verify/?token=<token>
    Expires in 24 hours.
    """
    verify_url     = request.build_absolute_uri(f'/verify/?token={token}')
    subject        = 'PhishGuard — Verify Your Agent Account'
    plain_message  = _verification_plain(username, verify_url)
    html_message   = _verification_html(username, verify_url)

    send_mail(
        subject        = subject,
        message        = plain_message,
        from_email     = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user_email],
        html_message   = html_message,
        fail_silently  = False,
    )


# ── Plain-text body ───────────────────────────────────────────

def _verification_plain(username, verify_url):
    return (
        f'PHISHGUARD SECURE TRANSMISSION\n\n'
        f'Agent {username},\n\n'
        f'Your account has been created. You must verify your email address '
        f'before you can access the system.\n\n'
        f'VERIFICATION LINK:\n{verify_url}\n\n'
        f'This link expires in 24 hours.\n\n'
        f'If you did not create this account, ignore this message.\n\n'
        f'— PhishGuard Security System'
    )


# ── HTML body ─────────────────────────────────────────────────

def _verification_html(username, verify_url):
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body       {{ background:#0a0f0a; color:#c8d8c8;
                  font-family:'Courier New',monospace; margin:0; padding:0; }}
    .wrap      {{ max-width:540px; margin:40px auto; padding:32px;
                  border:1px solid #00ff41;
                  box-shadow:0 0 24px rgba(0,255,65,.15); }}
    .logo      {{ font-size:1.4rem; font-weight:900; color:#00ff41;
                  letter-spacing:.3em; margin-bottom:4px; }}
    .tag       {{ font-size:.6rem; color:#ff3b3b; letter-spacing:.15em;
                  margin-bottom:24px; }}
    hr         {{ border:none; border-top:1px solid #1a2e1a; margin:20px 0; }}
    .label     {{ font-size:.65rem; color:#4a7a4a; letter-spacing:.15em;
                  margin-bottom:6px; }}
    .body-text {{ font-size:.82rem; line-height:1.8; color:#c8d8c8;
                  margin-bottom:20px; }}
    .btn       {{ display:inline-block; padding:14px 32px;
                  background:#00ff41; color:#000;
                  font-family:'Courier New',monospace;
                  font-size:.75rem; font-weight:700;
                  letter-spacing:.2em; text-decoration:none;
                  margin:8px 0 20px; }}
    .url-box   {{ background:#0d1a0d; border:1px solid #1a2e1a;
                  border-left:3px solid #00ff41;
                  padding:10px 14px; font-size:.65rem;
                  color:#4a7a4a; word-break:break-all;
                  margin-bottom:20px; }}
    .expire    {{ font-size:.65rem; color:#4a7a4a; letter-spacing:.08em; }}
    .footer    {{ font-size:.58rem; color:#2a3a2a; letter-spacing:.1em;
                  margin-top:28px; padding-top:16px;
                  border-top:1px solid #1a2e1a; }}
    .highlight {{ color:#00ff41; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="logo">PHISHGUARD</div>
    <div class="tag">// SECURE TRANSMISSION — AGENT VERIFICATION REQUIRED</div>
    <hr/>

    <div class="label">RECIPIENT</div>
    <p class="body-text">Agent <span class="highlight">{username}</span>,</p>

    <p class="body-text">
      Your PhishGuard agent account has been created and is pending activation.<br/>
      Click the button below to verify your email and activate your account.
    </p>

    <a href="{verify_url}" class="btn">&#9654; VERIFY AGENT ACCOUNT</a>

    <div class="label">DIRECT LINK</div>
    <div class="url-box">{verify_url}</div>

    <p class="expire">&#9889; This verification link expires in <strong>24 hours</strong>.</p>

    <hr/>
    <p class="body-text" style="font-size:.75rem;">
      If you did not create a PhishGuard account, disregard this message.
      No action is required.
    </p>

    <div class="footer">
      PHISHGUARD SECURITY SYSTEM — AUTOMATED TRANSMISSION<br/>
      DO NOT REPLY TO THIS EMAIL
    </div>
  </div>
</body>
</html>"""


# ── Password reset email (with username reminder) ─────────────

def send_password_reset_email(request, user_email, username, token):
    """
    Send a password reset email with a real token link.
    Also includes the agent codename in case they forgot it.
    Link: /reset/?token=<token>  — expires in 24 hours.
    """
    reset_url = request.build_absolute_uri(f'/reset/?token={token}')

    subject       = 'PhishGuard — Password Reset Request'
    plain_message = _reset_plain(username, reset_url)
    html_message  = _reset_html(username, reset_url)

    send_mail(
        subject        = subject,
        message        = plain_message,
        from_email     = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user_email],
        html_message   = html_message,
        fail_silently  = False,
    )


def _reset_plain(username, reset_url):
    return (
        f'PHISHGUARD SECURE TRANSMISSION\n\n'
        f'Agent {username},\n\n'
        f'A password reset was requested for your account.\n\n'
        f'YOUR AGENT CODENAME: {username}\n\n'
        f'PASSWORD RESET LINK:\n{reset_url}\n\n'
        f'If you did not request this reset, ignore this message.\n\n'
        f'— PhishGuard Security System'
    )


def _reset_html(username, reset_url):
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    body       {{ background:#0a0f0a; color:#c8d8c8;
                  font-family:'Courier New',monospace; margin:0; padding:0; }}
    .wrap      {{ max-width:540px; margin:40px auto; padding:32px;
                  border:1px solid #00ff41;
                  box-shadow:0 0 24px rgba(0,255,65,.15); }}
    .logo      {{ font-size:1.4rem; font-weight:900; color:#00ff41;
                  letter-spacing:.3em; margin-bottom:4px; }}
    .tag       {{ font-size:.6rem; color:#ff3b3b; letter-spacing:.15em;
                  margin-bottom:24px; }}
    hr         {{ border:none; border-top:1px solid #1a2e1a; margin:20px 0; }}
    .label     {{ font-size:.65rem; color:#4a7a4a; letter-spacing:.15em;
                  margin-bottom:6px; }}
    .body-text {{ font-size:.82rem; line-height:1.8; color:#c8d8c8;
                  margin-bottom:20px; }}
    .codename-box {{ background:#0d1a0d; border:1px solid #1a2e1a;
                  border-left:3px solid #00ff41;
                  padding:14px 18px; margin-bottom:20px; }}
    .codename-label {{ font-size:.6rem; color:#4a7a4a;
                  letter-spacing:.15em; margin-bottom:6px; }}
    .codename  {{ font-size:1.1rem; font-weight:700; color:#00ff41;
                  letter-spacing:.2em;
                  text-shadow:0 0 8px rgba(0,255,65,.4); }}
    .btn       {{ display:inline-block; padding:14px 32px;
                  background:#00ff41; color:#000;
                  font-family:'Courier New',monospace;
                  font-size:.75rem; font-weight:700;
                  letter-spacing:.2em; text-decoration:none;
                  margin:8px 0 20px; }}
    .footer    {{ font-size:.58rem; color:#2a3a2a; letter-spacing:.1em;
                  margin-top:28px; padding-top:16px;
                  border-top:1px solid #1a2e1a; }}
    .highlight {{ color:#00ff41; }}
    .warn      {{ font-size:.68rem; color:#4a7a4a; line-height:1.7; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="logo">PHISHGUARD</div>
    <div class="tag">// SECURE TRANSMISSION — PASSWORD RESET REQUEST</div>
    <hr/>

    <div class="label">RECIPIENT</div>
    <p class="body-text">Agent <span class="highlight">{username}</span>,</p>

    <p class="body-text">
      A password reset was requested for your PhishGuard account.<br/>
      In case you also forgot your codename, it is recorded below.
    </p>

    <div class="codename-box">
      <div class="codename-label">YOUR AGENT CODENAME</div>
      <div class="codename">{username}</div>
    </div>

    <div class="label">RESET LINK</div>
    <a href="{reset_url}" class="btn">&#9654; RESET PASSWORD</a>

    <hr/>
    <p class="warn">
      If you did not request a password reset, ignore this message.<br/>
      Your account remains secure and no changes have been made.
    </p>

    <div class="footer">
      PHISHGUARD SECURITY SYSTEM — AUTOMATED TRANSMISSION<br/>
      DO NOT REPLY TO THIS EMAIL
    </div>
  </div>
</body>
</html>"""