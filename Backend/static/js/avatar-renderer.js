'use strict';

const AvatarRenderer = (() => {

  function _setGrad(svgEl, id, stops) {
    if (!svgEl) return;
    stops.forEach((color, i) => {
      const s = svgEl.querySelector(`#${id} stop:nth-child(${i + 1})`);
      if (s) s.style.stopColor = color;
    });
  }

  function _ensureGrad(svgEl, id, stops) {
    if (!svgEl) return;
    let defs = svgEl.querySelector('defs');
    if (!defs) {
      defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
      svgEl.insertBefore(defs, svgEl.firstChild);
    }
    if (!svgEl.querySelector(`#${id}`)) {
      const grad = document.createElementNS('http://www.w3.org/2000/svg', 'radialGradient');
      grad.setAttribute('id', id);
      grad.setAttribute('cx', '35%'); grad.setAttribute('cy', '35%'); grad.setAttribute('r', '65%');
      stops.forEach((color, i) => {
        const s = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
        s.setAttribute('offset', `${Math.round(i / (stops.length - 1) * 100)}%`);
        s.style.stopColor = color;
        grad.appendChild(s);
      });
      defs.appendChild(grad);
    } else {
      _setGrad(svgEl, id, stops);
    }
  }

  function _catExprSVG(pos, expr) {
    const base = AV_CAT_EXPR[expr] || AV_CAT_EXPR.happy;
    const s  = pos.r / 27;
    const tx = pos.cx - 70 * s;
    const ty = pos.cy - 45 * s;
    return `<g transform="translate(${tx.toFixed(2)},${ty.toFixed(2)}) scale(${s})">${base}</g>`;
  }

  function _bichonEyesSVG(pos, expr) {
    const { cx, cy, r } = pos;
    const eyeOff = r * 0.38;
    const eyeR   = r * 0.22;
    const ey     = cy - r * 0.05;
    const lx     = cx - eyeOff;
    const rx     = cx + eyeOff;
    const hlR    = eyeR * 0.42;
    const hlOff  = eyeR * 0.38;

    if (expr === 'sleepy') {
      return `<path d="M${lx - eyeR} ${ey} Q${lx} ${ey - eyeR * 1.1} ${lx + eyeR} ${ey}" fill="#1a1008"/>` +
             `<path d="M${rx - eyeR} ${ey} Q${rx} ${ey - eyeR * 1.1} ${rx + eyeR} ${ey}" fill="#1a1008"/>`;
    }
    if (expr === 'wink') {
      return `<circle cx="${lx}" cy="${ey}" r="${eyeR}" fill="#1a1008"/>` +
             `<circle cx="${lx - hlOff}" cy="${ey - hlOff}" r="${hlR}" fill="white"/>` +
             `<path d="M${rx - eyeR} ${ey} Q${rx} ${ey + eyeR * 1.2} ${rx + eyeR} ${ey}" stroke="#1a1008" stroke-width="${eyeR * 0.5}" fill="none" stroke-linecap="round"/>`;
    }
    let brows = '';
    if (expr === 'focused') {
      brows = `<path d="M${lx - eyeR * 1.1} ${ey - eyeR * 1.3} Q${lx} ${ey - eyeR * 1.6} ${lx + eyeR * 1.1} ${ey - eyeR * 1.3}" stroke="#4a2808" stroke-width="${eyeR * 0.35}" fill="none" stroke-linecap="round"/>` +
              `<path d="M${rx - eyeR * 1.1} ${ey - eyeR * 1.3} Q${rx} ${ey - eyeR * 1.6} ${rx + eyeR * 1.1} ${ey - eyeR * 1.3}" stroke="#4a2808" stroke-width="${eyeR * 0.35}" fill="none" stroke-linecap="round"/>`;
    }
    return `${brows}` +
           `<circle cx="${lx}" cy="${ey}" r="${eyeR}" fill="#1a1008"/>` +
           `<circle cx="${rx}" cy="${ey}" r="${eyeR}" fill="#1a1008"/>` +
           `<circle cx="${lx - hlOff}" cy="${ey - hlOff}" r="${hlR}" fill="white"/>` +
           `<circle cx="${rx - hlOff}" cy="${ey - hlOff}" r="${hlR}" fill="white"/>`;
  }

  function _scaledHatSVG(pos, hatKey) {
    const h = AV_HAT_SVG[hatKey];
    if (!h) return '';
    const { hatTx, hatTy, hatS } = pos;
    return `<g transform="translate(${hatTx},${hatTy}) scale(${hatS})">${h}</g>`;
  }

  function _scaledAccSVG(pos, accKey) {
    const a = AV_ACC_SVG[accKey];
    if (!a) return '';
    const s  = pos.r / 27;
    const tx = pos.cx - 70 * s;
    const ty = pos.cy - 45 * s;
    return `<g transform="translate(${tx.toFixed(2)},${ty.toFixed(2)}) scale(${s})">${a}</g>`;
  }

  function _buildBichonTab(p, pos, cust) {
    const coat = AV_BICHON_COAT[cust.coatColor] || AV_BICHON_COAT.white;
    const { cx, cy, r, bodyCx, bodyCy, bodyRx, bodyRy } = pos;
    const gradId = `${p}_bh`;
    const c0 = coat.h[0], c1 = coat.h[1], c2 = coat.h[2];

    const fluffy = () => {
      const puffs = [];
      const angles = [0, 40, 80, 120, 160, 200, 240, 280, 320];
      angles.forEach(a => {
        const rad = a * Math.PI / 180;
        const pr  = r * 0.92;
        const px  = cx + Math.cos(rad) * pr;
        const py  = cy + Math.sin(rad) * pr;
        puffs.push(`<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${(r * 0.36).toFixed(1)}" fill="url(#${gradId})"/>`);
      });
      return puffs.join('');
    };

    const earsHTML = `<circle cx="${(cx - r * 0.62).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.28).toFixed(1)}" fill="url(#${gradId})"/>` +
                     `<circle cx="${(cx + r * 0.62).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.28).toFixed(1)}" fill="url(#${gradId})"/>`;
    const faceHTML = `<circle cx="${cx}" cy="${cy}" r="${(r * 0.78).toFixed(1)}" fill="url(#${gradId})"/>`;
    const noseHTML = `<ellipse cx="${cx}" cy="${(cy + r * 0.15).toFixed(1)}" rx="${(r * 0.1).toFixed(1)}" ry="${(r * 0.07).toFixed(1)}" fill="#d08080"/>` +
                     `<path d="M${cx} ${(cy + r * 0.15 + r * 0.07).toFixed(1)} Q${(cx - r * 0.12).toFixed(1)} ${(cy + r * 0.32).toFixed(1)} ${(cx - r * 0.22).toFixed(1)} ${(cy + r * 0.25).toFixed(1)}" stroke="#c07070" stroke-width="1.2" fill="none" stroke-linecap="round"/>` +
                     `<path d="M${cx} ${(cy + r * 0.15 + r * 0.07).toFixed(1)} Q${(cx + r * 0.12).toFixed(1)} ${(cy + r * 0.32).toFixed(1)} ${(cx + r * 0.22).toFixed(1)} ${(cy + r * 0.25).toFixed(1)}" stroke="#c07070" stroke-width="1.2" fill="none" stroke-linecap="round"/>`;
    const bodyHTML = `<ellipse cx="${bodyCx}" cy="${bodyCy}" rx="${(bodyRx * 1.1).toFixed(1)}" ry="${(bodyRy * 1.1).toFixed(1)}" fill="url(#${gradId})"/>`;
    const eyesHTML = _bichonEyesSVG(pos, cust.expression || 'happy');
    const hatHTML  = _scaledHatSVG(pos, cust.hat || 'none');
    const accHTML  = _scaledAccSVG(pos, cust.accessory || 'none');

    return `<g id="${p}-bichon-body">${fluffy()}${earsHTML}${faceHTML}${bodyHTML}${noseHTML}</g>` +
           `<g id="${p}-bichon-eyes">${eyesHTML}</g>` +
           `<g id="${p}-bichon-hat">${hatHTML}</g>` +
           `<g id="${p}-bichon-acc">${accHTML}</g>`;
  }

  function _buildMainBichon(cust) {
    const coat = AV_BICHON_COAT[cust.coatColor] || AV_BICHON_COAT.white;
    const c0 = coat.h[0], c1 = coat.h[1], c2 = coat.h[2];
    const cx = 70, cy = 45, r = 27;

    const puffAngles = [0, 36, 72, 108, 144, 180, 216, 252, 288, 324];
    const puffs = puffAngles.map(a => {
      const rad = a * Math.PI / 180;
      const pr = r * 0.9;
      const px = cx + Math.cos(rad) * pr;
      const py = cy + Math.sin(rad) * pr;
      return `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${(r * 0.38).toFixed(1)}" fill="url(#bHead)"/>`;
    }).join('');

    const outfit = AV_OUTFIT_SVG[cust.outfit] || '';
    const hat    = AV_HAT_SVG[cust.hat] || '';
    const acc    = AV_ACC_SVG[cust.accessory] || '';
    const expr   = AV_BICHON_EXPR[cust.expression] || AV_BICHON_EXPR.happy;

    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 122" width="160" height="122">
  <defs>
    <radialGradient id="bHead" cx="35%" cy="35%" r="65%">
      <stop offset="0%" style="stop-color:${c0}"/>
      <stop offset="55%" style="stop-color:${c1}"/>
      <stop offset="100%" style="stop-color:${c2}"/>
    </radialGradient>
  </defs>
  <!-- laptop -->
  <rect x="22" y="88" width="116" height="26" rx="5" fill="#2c2c3a"/>
  <rect x="30" y="72" width="100" height="52" rx="4" fill="#1a1a28"/>
  <rect x="33" y="75" width="94" height="46" rx="2" fill="#0d1117"/>
  <circle cx="80" cy="118" r="3" fill="#3a3a50"/>
  <!-- outfit layer -->
  <g id="bichon-outfit-overlay">${outfit}</g>
  <!-- body fluffy -->
  <ellipse cx="70" cy="96" rx="34" ry="16" fill="url(#bHead)"/>
  <ellipse cx="50" cy="88" rx="12" ry="22" fill="url(#bHead)"/>
  <ellipse cx="90" cy="88" rx="12" ry="22" fill="url(#bHead)"/>
  <!-- head fluffy -->
  ${puffs}
  <!-- ear puffs -->
  <circle cx="${(cx - r * 0.72).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.32).toFixed(1)}" fill="url(#bHead)"/>
  <circle cx="${(cx + r * 0.72).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.32).toFixed(1)}" fill="url(#bHead)"/>
  <!-- face base -->
  <circle cx="${cx}" cy="${cy}" r="${(r * 0.82).toFixed(1)}" fill="url(#bHead)"/>
  <!-- cheeks -->
  <circle cx="${(cx - r * 0.52).toFixed(1)}" cy="${(cy + r * 0.22).toFixed(1)}" r="${(r * 0.22).toFixed(1)}" fill="url(#bHead)"/>
  <circle cx="${(cx + r * 0.52).toFixed(1)}" cy="${(cy + r * 0.22).toFixed(1)}" r="${(r * 0.22).toFixed(1)}" fill="url(#bHead)"/>
  <!-- blush -->
  <ellipse cx="58" cy="50" rx="5" ry="3" fill="#ffb0c8" opacity="0.4"/>
  <ellipse cx="82" cy="50" rx="5" ry="3" fill="#ffb0c8" opacity="0.4"/>
  <!-- eyes -->
  <g id="bichon-eyes-open">${expr}</g>
  <!-- nose -->
  <ellipse cx="70" cy="52" rx="3.5" ry="2.5" fill="#d08080"/>
  <path d="M70 54.5 Q64 58 60 55" stroke="#c07070" stroke-width="1.4" fill="none" stroke-linecap="round"/>
  <path d="M70 54.5 Q76 58 80 55" stroke="#c07070" stroke-width="1.4" fill="none" stroke-linecap="round"/>
  <!-- hat overlay -->
  <g id="bichon-hat-overlay">${hat}</g>
  <!-- acc overlay -->
  <g id="bichon-acc-overlay">${acc}</g>
</svg>`;
  }

  function _buildPreview(state) {
    const charId = state.selectedCharacter;
    const cust   = state.customization[charId];

    if (charId === 'bichon') {
      const coat = AV_BICHON_COAT[cust.coatColor] || AV_BICHON_COAT.white;
      const c0 = coat.h[0], c1 = coat.h[1], c2 = coat.h[2];
      const cx = 70, cy = 52, r = 30;
      const puffAngles = [0, 36, 72, 108, 144, 180, 216, 252, 288, 324];
      const puffs = puffAngles.map(a => {
        const rad = a * Math.PI / 180;
        const px = cx + Math.cos(rad) * r * 0.9;
        const py = cy + Math.sin(rad) * r * 0.9;
        return `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${(r * 0.38).toFixed(1)}" fill="url(#pvbh)"/>`;
      }).join('');
      const expr   = AV_BICHON_EXPR[cust.expression] || AV_BICHON_EXPR.happy;
      const exprScaled = `<g transform="translate(${cx-70},${cy-52}) scale(${r/27})">${expr}</g>`;
      const hat    = AV_HAT_SVG[cust.hat] || '';
      const hatPos = { hatTx: 10, hatTy: 5, hatS: 1.1 };
      const hatSVG = hat ? `<g transform="translate(${hatPos.hatTx},${hatPos.hatTy}) scale(${hatPos.hatS})">${hat}</g>` : '';
      const acc    = AV_ACC_SVG[cust.accessory] || '';
      const outfit = AV_OUTFIT_SVG[cust.outfit] || '';
      const outfitScaled = outfit ? `<g transform="translate(0,30) scale(0.9)">${outfit}</g>` : '';
      return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 130" width="140" height="130">
  <defs><radialGradient id="pvbh" cx="35%" cy="35%" r="65%">
    <stop offset="0%" style="stop-color:${c0}"/>
    <stop offset="55%" style="stop-color:${c1}"/>
    <stop offset="100%" style="stop-color:${c2}"/>
  </radialGradient></defs>
  ${outfitScaled}
  <ellipse cx="${cx}" cy="${cy+55}" rx="32" ry="15" fill="url(#pvbh)"/>
  <ellipse cx="${cx-22}" cy="${cy+44}" rx="12" ry="20" fill="url(#pvbh)"/>
  <ellipse cx="${cx+22}" cy="${cy+44}" rx="12" ry="20" fill="url(#pvbh)"/>
  ${puffs}
  <circle cx="${(cx - r * 0.72).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.32).toFixed(1)}" fill="url(#pvbh)"/>
  <circle cx="${(cx + r * 0.72).toFixed(1)}" cy="${(cy - r * 0.72).toFixed(1)}" r="${(r * 0.32).toFixed(1)}" fill="url(#pvbh)"/>
  <circle cx="${cx}" cy="${cy}" r="${(r * 0.82).toFixed(1)}" fill="url(#pvbh)"/>
  <circle cx="${(cx - r * 0.52).toFixed(1)}" cy="${(cy + r * 0.22).toFixed(1)}" r="${(r * 0.22).toFixed(1)}" fill="url(#pvbh)"/>
  <circle cx="${(cx + r * 0.52).toFixed(1)}" cy="${(cy + r * 0.22).toFixed(1)}" r="${(r * 0.22).toFixed(1)}" fill="url(#pvbh)"/>
  <ellipse cx="${cx-14}" cy="${cy+6}" rx="5" ry="3" fill="#ffb0c8" opacity="0.4"/>
  <ellipse cx="${cx+14}" cy="${cy+6}" rx="5" ry="3" fill="#ffb0c8" opacity="0.4"/>
  ${exprScaled}
  <ellipse cx="${cx}" cy="${(cy + r * 0.18).toFixed(1)}" rx="3.8" ry="2.7" fill="#d08080"/>
  <path d="M${cx} ${(cy + r * 0.18 + 2.7).toFixed(1)} Q${cx-7} ${(cy + r * 0.4).toFixed(1)} ${cx-12} ${(cy + r * 0.32).toFixed(1)}" stroke="#c07070" stroke-width="1.4" fill="none" stroke-linecap="round"/>
  <path d="M${cx} ${(cy + r * 0.18 + 2.7).toFixed(1)} Q${cx+7} ${(cy + r * 0.4).toFixed(1)} ${cx+12} ${(cy + r * 0.32).toFixed(1)}" stroke="#c07070" stroke-width="1.4" fill="none" stroke-linecap="round"/>
  ${hatSVG}
  ${acc}
</svg>`;
    }

    // cat preview
    const body   = AV_CAT_BODY[cust.bodyColor] || AV_CAT_BODY.orange;
    const ear    = AV_CAT_EAR[cust.earColor]   || AV_CAT_EAR.pink;
    const c0 = body.h[0], c1 = body.h[1], c2 = body.h[2];
    const b0 = body.b[0], b1 = body.b[1], b2 = body.b[2];
    const e0 = body.e[0], e1 = body.e[1];
    const expr   = AV_CAT_EXPR[cust.expression] || AV_CAT_EXPR.happy;
    const hat    = AV_HAT_SVG[cust.hat] || '';
    const hatSVG = hat ? `<g transform="translate(10,5) scale(1.1)">${hat}</g>` : '';
    const acc    = AV_ACC_SVG[cust.accessory] || '';
    const outfit = AV_OUTFIT_SVG[cust.outfit] || '';
    const outfitScaled = outfit ? `<g transform="translate(0,30) scale(0.9)">${outfit}</g>` : '';
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 130" width="140" height="130">
  <defs>
    <radialGradient id="pvHead" cx="35%" cy="35%" r="65%">
      <stop offset="0%" style="stop-color:${c0}"/>
      <stop offset="55%" style="stop-color:${c1}"/>
      <stop offset="100%" style="stop-color:${c2}"/>
    </radialGradient>
    <radialGradient id="pvBody" cx="35%" cy="30%" r="65%">
      <stop offset="0%" style="stop-color:${b0}"/>
      <stop offset="55%" style="stop-color:${b1}"/>
      <stop offset="100%" style="stop-color:${b2}"/>
    </radialGradient>
    <radialGradient id="pvEar" cx="50%" cy="50%" r="60%">
      <stop offset="0%" style="stop-color:${ear[0]}"/>
      <stop offset="100%" style="stop-color:${ear[1]}"/>
    </radialGradient>
    <radialGradient id="pvEye" cx="40%" cy="30%" r="70%">
      <stop offset="0%" style="stop-color:${e0}"/>
      <stop offset="100%" style="stop-color:${e1}"/>
    </radialGradient>
  </defs>
  ${outfitScaled}
  <ellipse cx="70" cy="108" rx="32" ry="13" fill="url(#pvBody)"/>
  <ellipse cx="52" cy="95" rx="11" ry="18" fill="url(#pvBody)"/>
  <ellipse cx="88" cy="95" rx="11" ry="18" fill="url(#pvBody)"/>
  <polygon points="48,32 40,10 62,24" fill="url(#pvHead)"/>
  <polygon points="92,32 100,10 78,24" fill="url(#pvHead)"/>
  <polygon points="50,31 43,15 60,25" fill="url(#pvEar)"/>
  <polygon points="90,31 97,15 80,25" fill="url(#pvEar)"/>
  <circle cx="70" cy="52" r="30" fill="url(#pvHead)"/>
  <ellipse cx="56" cy="58" rx="7.5" ry="5.5" fill="url(#pvEye)"/>
  <ellipse cx="84" cy="58" rx="7.5" ry="5.5" fill="url(#pvEye)"/>
  ${expr}
  ${hatSVG}
  ${acc}
</svg>`;
  }

  function _applyCatColors(state) {
    const cust = state.customization.cat;
    const body = AV_CAT_BODY[cust.bodyColor] || AV_CAT_BODY.orange;
    const ear  = AV_CAT_EAR[cust.earColor]   || AV_CAT_EAR.pink;

    // Main SVG: cHead, cBody, cEar (outer ear from body palette), cInner (inner ear color)
    const mainSVG = document.getElementById('cat-wrap');
    if (mainSVG) {
      _setGrad(mainSVG, 'cHead',  body.h);
      _setGrad(mainSVG, 'cBody',  body.b);
      _setGrad(mainSVG, 'cEar',   body.e);
      _setGrad(mainSVG, 'cInner', ear);
    }

    // Tab SVGs: {p}_h, {p}_b, {p}_ie (inner ear)
    Object.keys(AV_TAB_POS).forEach(p => {
      const svgEl = document.getElementById(`${p}-wrap`);
      if (!svgEl) return;
      _setGrad(svgEl, `${p}_h`,  body.h);
      _setGrad(svgEl, `${p}_b`,  body.b);
      _setGrad(svgEl, `${p}_ie`, ear);
    });
  }

  function _applyCatExpression(state) {
    const expr = state.customization.cat.expression || 'happy';
    const mainEyes = document.getElementById('cat-eyes-open');
    if (mainEyes) mainEyes.innerHTML = AV_CAT_EXPR[expr] || AV_CAT_EXPR.happy;

    Object.keys(AV_TAB_POS).forEach(p => {
      const g = document.getElementById(`${p}-eyes-ov`);
      if (!g) return;
      const pos = AV_TAB_POS[p];
      g.innerHTML = _catExprSVG(pos, expr);
    });
  }

  function _applyCatHat(state) {
    const hat = state.customization.cat.hat || 'none';
    const mainHat = document.getElementById('cat-hat-overlay');
    if (mainHat) mainHat.innerHTML = AV_HAT_SVG[hat] || '';

    Object.keys(AV_TAB_POS).forEach(p => {
      const g = document.getElementById(`${p}-hat-ov`);
      if (!g) return;
      const pos = AV_TAB_POS[p];
      g.innerHTML = _scaledHatSVG(pos, hat);
    });
  }

  function _applyCatAcc(state) {
    const acc = state.customization.cat.accessory || 'none';
    const mainAcc = document.getElementById('cat-acc-overlay');
    if (mainAcc) mainAcc.innerHTML = AV_ACC_SVG[acc] || '';

    Object.keys(AV_TAB_POS).forEach(p => {
      const g = document.getElementById(`${p}-acc-ov`);
      if (!g) return;
      const pos = AV_TAB_POS[p];
      g.innerHTML = _scaledAccSVG(pos, acc);
    });
  }

  function _applyCatOutfit(state) {
    const outfit = state.customization.cat.outfit || 'none';
    const mainOutfit = document.getElementById('cat-outfit-overlay');
    if (mainOutfit) mainOutfit.innerHTML = AV_OUTFIT_SVG[outfit] || '';
  }

  function _applyBichonMain(state) {
    const cust  = state.customization.bichon;
    const slot  = document.getElementById('main-avatar-slot');
    if (!slot) return;

    let outer = document.getElementById('bichon-wrap-outer');
    if (!outer) {
      outer = document.createElement('div');
      outer.id = 'bichon-wrap-outer';
      outer.style.cssText = 'position:absolute;top:0;left:0;width:160px;height:122px;display:none;';
      slot.style.position = 'relative';
      slot.appendChild(outer);
    }
    outer.innerHTML = _buildMainBichon(cust);
  }

  function _applyBichonTabs(state) {
    const cust = state.customization.bichon;
    Object.keys(AV_TAB_POS).forEach(p => {
      const g = document.getElementById(`${p}-bichon`);
      if (!g) return;
      const svgEl = document.getElementById(`${p}-wrap`);
      if (!svgEl) return;
      const pos = AV_TAB_POS[p];
      const coat = AV_BICHON_COAT[cust.coatColor] || AV_BICHON_COAT.white;
      _ensureGrad(svgEl, `${p}_bh`, coat.h);
      if (!g.dataset.rendered) {
        g.innerHTML = _buildBichonTab(p, pos, cust);
        g.dataset.rendered = '1';
      } else {
        _ensureGrad(svgEl, `${p}_bh`, coat.h);
        const eyesG = document.getElementById(`${p}-bichon-eyes`);
        if (eyesG) eyesG.innerHTML = _bichonEyesSVG(pos, cust.expression || 'happy');
        const hatG = document.getElementById(`${p}-bichon-hat`);
        if (hatG) hatG.innerHTML = _scaledHatSVG(pos, cust.hat || 'none');
        const accG = document.getElementById(`${p}-bichon-acc`);
        if (accG) accG.innerHTML = _scaledAccSVG(pos, cust.accessory || 'none');
      }
    });
  }

  function _toggleMain(charId) {
    const catWrap = document.getElementById('cat-wrap');
    const bichonOuter = document.getElementById('bichon-wrap-outer');
    if (catWrap) catWrap.style.display = charId === 'cat' ? '' : 'none';
    if (bichonOuter) bichonOuter.style.display = charId === 'bichon' ? '' : 'none';
  }

  function _toggleTabs(charId) {
    document.querySelectorAll('.char-cat-elems').forEach(el => {
      el.style.display = charId === 'cat' ? '' : 'none';
    });
    document.querySelectorAll('.char-bichon-elems').forEach(el => {
      el.style.display = charId === 'bichon' ? '' : 'none';
    });
  }

  function applyAll(state) {
    const charId = state.selectedCharacter;
    _toggleTabs(charId);

    if (charId === 'cat') {
      _applyCatColors(state);
      _applyCatExpression(state);
      _applyCatHat(state);
      _applyCatAcc(state);
      _applyCatOutfit(state);
    } else if (charId === 'bichon') {
      _applyBichonMain(state);
      _applyBichonTabs(state);
    }
    _toggleMain(charId);
  }

  function renderPreview(state) {
    const container = document.getElementById('av-preview-container');
    if (!container) return;
    container.innerHTML = _buildPreview(state);
  }

  return { applyAll, renderPreview };
})();
