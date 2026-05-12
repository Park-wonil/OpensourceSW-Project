'use strict';

const AvatarCustomizer = (() => {

  function open() {
    const overlay = document.getElementById('avatar-customizer-overlay');
    if (overlay) {
      overlay.classList.add('av-open');
      refresh();
    }
  }

  function close() {
    const overlay = document.getElementById('avatar-customizer-overlay');
    if (overlay) overlay.classList.remove('av-open');
  }

  function refresh() {
    _updateCharTabs();
    _renderOptions();
    AvatarRenderer.renderPreview(AvatarSystem.get());
  }

  function refreshPreview() {
    AvatarRenderer.renderPreview(AvatarSystem.get());
    _updateSelected();
  }

  function _updateCharTabs() {
    const state = AvatarSystem.get();
    document.querySelectorAll('[data-av-char]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.avChar === state.selectedCharacter);
    });
  }

  function _updateSelected() {
    const state  = AvatarSystem.get();
    const charId = state.selectedCharacter;
    const cust   = state.customization[charId];
    document.querySelectorAll('[data-av-key]').forEach(el => {
      const key = el.dataset.avKey;
      const val = el.dataset.avVal;
      el.classList.toggle('selected', cust[key] === val);
    });
  }

  function _renderOptions() {
    const panel = document.getElementById('av-options-panel');
    if (!panel) return;

    const state  = AvatarSystem.get();
    const charId = state.selectedCharacter;
    const cust   = state.customization[charId];
    const config = CHARACTER_CONFIGS[charId];
    if (!config) return;

    let html = '';

    config.colorGroups.forEach(group => {
      html += `<div class="av-section">`;
      html += `<div class="av-section-label">${group.label}</div>`;
      html += `<div class="av-chips-row">`;
      group.options.forEach(opt => {
        const sel   = cust[group.key] === opt.id ? ' selected' : '';
        const extra = opt.outline ? ' av-chip-outline' : '';
        html += `<button class="av-chip${sel}${extra}" data-av-key="${group.key}" data-av-val="${opt.id}"
          style="background:${opt.color};" title="${opt.label}"
          onclick="AvatarSystem.setOption('${group.key}','${opt.id}')"></button>`;
      });
      html += `</div></div>`;
    });

    SHARED_OPTIONS.forEach(group => {
      html += `<div class="av-section">`;
      html += `<div class="av-section-label">${group.label}</div>`;
      html += `<div class="av-cards-row">`;
      group.options.forEach(opt => {
        const sel = cust[group.key] === opt.id ? ' selected' : '';
        html += `<button class="av-card${sel}" data-av-key="${group.key}" data-av-val="${opt.id}"
          onclick="AvatarSystem.setOption('${group.key}','${opt.id}')">
          <span class="av-card-emoji">${opt.emoji}</span>
          <span class="av-card-label">${opt.label}</span>
        </button>`;
      });
      html += `</div></div>`;
    });

    panel.innerHTML = html;
  }

  return { open, close, refresh, refreshPreview };
})();
