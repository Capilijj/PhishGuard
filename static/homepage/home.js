window.addEventListener('DOMContentLoaded', function () {
  // XP Bar Animation
  var fill = document.getElementById('xpFill');
  if (fill) {
    var target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(function () { fill.style.width = target; }, 350);
  }

  // Agent Dropdown Menu
  var agentBox = document.querySelector('.pg-header__agent-dropdown');
  var menu = document.querySelector('.pg-header__agent-menu');
  if (agentBox && menu) {
    agentBox.addEventListener('mouseenter', function () {
      menu.classList.add('visible');
    });
    agentBox.addEventListener('mouseleave', function () {
      menu.classList.remove('visible');
    });
  }

  // Modal Core Logic
  var modal = document.getElementById('pg-modal');
  var modalContent = document.querySelector('.pg-modal-content');
  var modalBody = document.getElementById('pg-modal-body');
  var modalClose = document.getElementById('pg-modal-close');

  function showModal(content, wide) {
    modalBody.innerHTML = content;
    if (wide) {
      modalContent.classList.add('pg-modal-content--wide');
    } else {
      modalContent.classList.remove('pg-modal-content--wide');
    }
    modal.classList.add('show');
  }

  function hideModal() {
    modal.classList.remove('show');
  }

  modalClose.addEventListener('click', hideModal);
  modal.addEventListener('click', function (e) {
    if (e.target === modal) hideModal();
  });

  // Separate Logic for "Play Now" / Missions
  function showMissionModal() {
    var missionSection = document.querySelector('.pg-missions');
    if (!missionSection) return;
    
    // I-clone ang mission grid para sa modal
    var clone = missionSection.cloneNode(true);
    clone.style.width = '100%';
    
    // I-call ang showModal na may 'true' para sa WIDE mode
    showModal(
      '<div class="pg-mission-popup">' +
      '<div class="pg-modal-title">SELECT A MISSION</div>' +
      clone.outerHTML +
      '</div>',
      true
    );
  }

  // Event listener para sa Play Button sa Banner
  var bannerButton = document.getElementById('pg-banner-play-btn');
  if (bannerButton) {
    bannerButton.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation(); 
      showMissionModal();
    });
  }

  // Standard click listeners para sa ibang cards (Stats, Activity, Status)
  var containers = document.querySelectorAll('.pg-stat, .pg-activity, .pg-status');
  containers.forEach(function (container) {
    container.addEventListener('click', function (e) {
      var clone = container.cloneNode(true);
      clone.style.transform = 'none';
      clone.style.boxShadow = 'none';
      clone.style.cursor = 'default';
      
      // Gawing wide lang kung status o activity ang clinick
      var widePopup = container.classList.contains('pg-status') || container.classList.contains('pg-activity');
      showModal(clone.outerHTML, widePopup);
    });
  });

  // Mission data para sa preview modal
  var missionData = {
    'EMAIL DETECTOR': {
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
      level: 'LVL 1',
      color: 'green',
      difficulty: 'ROOKIE',
      briefing: 'Intelligence reports incoming phishing emails targeting HQ personnel. Your mission: analyze email headers, sender patterns, and embedded links to neutralize the threat before it breaches our defenses.',
      desc: 'Spot the fake emails from boss. Analyze headers, links, and sender patterns to identify phishing attempts.',
      url: '#email-detector'
    },
    'ID SCANNER': {
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2"/><path d="M14 9h4M14 12h4M14 15h2"/></svg>',
      level: 'LVL 5',
      color: 'yellow',
      difficulty: 'FIELD AGENT',
      briefing: 'Imposters have been detected attempting to infiltrate secure sectors using forged digital IDs. Scan and verify visitor credentials — one slip and the mole gets through.',
      desc: 'Scan visitor cards for forgery. Verify digital identities and detect impersonation attempts.',
      url: '#id-scanner'
    },
    'BADGE CRACK': {
      icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
      level: 'LVL 10',
      color: 'red',
      difficulty: 'ELITE',
      briefing: 'A mole has embedded fake authentication tokens deep within the system. You have minutes to crack the chain and expose the imposter badge before it grants unauthorized access to the mainframe.',
      desc: 'Identify the imposter tokens. Crack the authentication chain before the mole gets through the gate.',
      url: '#badge-crack'
    }
  };

  var colorMap = {
    green:  { hex: '#00ff41', glow: 'rgba(0,255,65,.25)',  bg: 'rgba(0,255,65,.07)'  },
    yellow: { hex: '#ffd600', glow: 'rgba(255,214,0,.25)', bg: 'rgba(255,214,0,.07)' },
    red:    { hex: '#ff3b3b', glow: 'rgba(255,59,59,.25)', bg: 'rgba(255,59,59,.07)' }
  };

  function showMissionPreview(missionName, isLocked, lockLevel) {
    var m = missionData[missionName];
    if (!m) return;
    var c = colorMap[m.color];

    var lockedHTML = '';
    if (isLocked) {
      lockedHTML = '<div class="pg-preview__locked-warn">⚠ REACH ' + lockLevel + ' TO UNLOCK THIS MISSION</div>';
    }

    var startBtn = isLocked
      ? '<button class="pg-preview__btn pg-preview__btn--disabled" disabled>🔒 LOCKED</button>'
      : '<a class="pg-preview__btn" href="' + m.url + '">▶ START MISSION</a>';

    var html =
      '<div class="pg-preview" style="--preview-color:' + c.hex + ';--preview-glow:' + c.glow + ';--preview-bg:' + c.bg + '">' +
        '<div class="pg-preview__header">' +
          '<div class="pg-preview__icon">' + m.icon + '</div>' +
          '<div class="pg-preview__title-wrap">' +
            '<div class="pg-preview__name">' + missionName + '</div>' +
            '<div class="pg-preview__badges">' +
              '<span class="pg-preview__badge">' + m.level + '</span>' +
              '<span class="pg-preview__badge pg-preview__badge--diff">' + m.difficulty + '</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div class="pg-preview__divider"></div>' +
        '<div class="pg-preview__section-label">MISSION BRIEFING</div>' +
        '<div class="pg-preview__briefing">' + m.briefing + '</div>' +
        '<div class="pg-preview__section-label" style="margin-top:1rem">OBJECTIVE</div>' +
        '<div class="pg-preview__objective">' + m.desc + '</div>' +
        lockedHTML +
        '<div class="pg-preview__actions">' +
          '<button class="pg-preview__btn pg-preview__btn--cancel" id="pg-preview-cancel">✕ CANCEL</button>' +
          startBtn +
        '</div>' +
      '</div>';

    showModal(html, false);

    var cancelBtn = document.getElementById('pg-preview-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', hideModal);
  }

  // Individual mission click listeners
  var missionCards = document.querySelectorAll('.pg-missions .pg-mission');
  missionCards.forEach(function (mission) {
    mission.addEventListener('click', function (e) {
      e.preventDefault();
      var nameEl = mission.querySelector('.pg-mission__name');
      if (!nameEl) return;
      var name = nameEl.textContent.trim();
      var locked = !!mission.querySelector('.pg-mission__locked');
      var lockLevelEl = mission.querySelector('.pg-mission__lvl');
      var lockLevel = lockLevelEl ? lockLevelEl.textContent.trim() : '';
      showMissionPreview(name, locked, lockLevel);
    });
  });
});

window.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Toggle Logic
  const mobileToggle = document.getElementById('pg-mobile-toggle');
  const navMenu = document.getElementById('pg-nav-menu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      navMenu.classList.toggle('active');
      mobileToggle.classList.toggle('open');
      
      const spans = mobileToggle.querySelectorAll('span');
      if (mobileToggle.classList.contains('open')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(4px, -4px)';
      } else {
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[2].style.transform = 'none';
      }
    });
  }

  // 2. Click outside to close
  document.addEventListener('click', function(e) {
    if (navMenu && !navMenu.contains(e.target) && !mobileToggle.contains(e.target)) {
      navMenu.classList.remove('active');
      mobileToggle.classList.remove('open');
      const spans = mobileToggle.querySelectorAll('span');
      if(spans.length > 0) {
        spans[0].style.transform = 'none';
        spans[1].style.opacity = '1';
        spans[2].style.transform = 'none';
      }
    }
  });

  // 3. XP Bar Animation
  var fill = document.getElementById('xpFill');
  if (fill) {
    var target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(function () { fill.style.width = target; }, 350);
  }
});