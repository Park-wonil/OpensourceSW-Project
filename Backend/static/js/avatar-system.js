'use strict';

const AV_CAT_BODY = {
  orange: { h:['#ffe0a0','#f4a460','#c07030'], b:['#ffc870','#f4a460','#b86820'], e:['#ffe0c0','#f4a060'] },
  gray:   { h:['#d8d8e0','#9090a0','#606070'], b:['#c8c8d8','#8888a0','#585868'], e:['#d0d0e0','#8888a0'] },
  cream:  { h:['#fff8e8','#f5e0b0','#d8c090'], b:['#fff0d0','#eed8a0','#c8a870'], e:['#fff0d8','#eeda98'] },
  brown:  { h:['#d09060','#9b6a3e','#6b4020'], b:['#c08050','#9b6a3e','#5a3018'], e:['#c08050','#9b6a3e'] },
  black:  { h:['#606070','#404055','#282835'], b:['#505060','#383850','#202030'], e:['#505060','#383850'] },
  white:  { h:['#ffffff','#f0f0f0','#d8d8dc'], b:['#f8f8fc','#e8e8ee','#d0d0d8'], e:['#f8f8fc','#e8e8ee'] },
};

const AV_CAT_EAR = {
  pink:  ['#ffd0dc','#f070a0'],
  mint:  ['#b0f0e0','#40b898'],
  lilac: ['#d8c8f0','#9870c0'],
  coral: ['#ffc0b0','#e07060'],
};

const AV_BICHON_COAT = {
  white:  { h:['#ffffff','#f4f5f8','#e4e6ec'] },
  cream:  { h:['#fffaf0','#f5e8c4','#ded0a8'] },
  golden: { h:['#fff8d8','#f5d07a','#d0a840'] },
  silver: { h:['#f2f4f8','#d5dae5','#b0b8c8'] },
};

const AV_HAT_SVG = {
  none: '',
  party:  `<path d="M70 6 L52 29 L88 29Z" fill="#ff5090"/><path d="M63 8 L54 26 L59 26 L67 8Z" fill="#ffe050" opacity="0.82"/><path d="M75 8 L69 26 L74 26 L80 8Z" fill="#50c0ff" opacity="0.82"/><ellipse cx="70" cy="29" rx="19" ry="5" fill="#ff5090"/><circle cx="70" cy="4" r="5" fill="#ffe8a0"/>`,
  wizard: `<path d="M70 4 L50 30 L90 30Z" fill="#2a1a80"/><ellipse cx="70" cy="30" rx="21" ry="5.5" fill="#3a28a0"/><polygon points="70,8 72,13 77,13 73,16 74.5,21 70,18 65.5,21 67,16 63,13 68,13" fill="#ffd700"/>`,
  crown:  `<polygon points="53,29 53,11 62,19 70,8 78,19 87,11 87,29" fill="#ffd700"/><rect x="53" y="24" width="34" height="7" rx="2" fill="#e6b000"/><circle cx="70" cy="9.5" r="3.5" fill="#ff4060"/><circle cx="57" cy="17.5" r="2.5" fill="#60a8ff"/><circle cx="83" cy="17.5" r="2.5" fill="#60a8ff"/>`,
  santa:  `<path d="M70 4 L51 31 L89 31Z" fill="#cc1010"/><ellipse cx="70" cy="31" rx="20" ry="5.5" fill="white"/><circle cx="70" cy="2" r="5.5" fill="white"/>`,
  beanie: `<path d="M52 30 Q52 8 70 8 Q88 8 88 30Z" fill="#4a68e8"/><rect x="50" y="26" width="40" height="7" rx="3.5" fill="#3858d8"/><circle cx="70" cy="7" r="7" fill="#5a78f8"/>`,
  beret:  `<ellipse cx="70" cy="23" rx="24" ry="10" fill="#cc3068"/><ellipse cx="70" cy="25.5" rx="23" ry="5.5" fill="#b82858"/><circle cx="81" cy="16" r="4.5" fill="#dd4078"/>`,
};

const AV_ACC_SVG = {
  none: '',
  glasses: `<rect x="55" y="38" width="14" height="11" rx="5.5" fill="rgba(28,28,40,0.12)" stroke="#303848" stroke-width="1.8"/><rect x="71" y="38" width="14" height="11" rx="5.5" fill="rgba(28,28,40,0.12)" stroke="#303848" stroke-width="1.8"/><line x1="56" y1="43.5" x2="53" y2="41.5" stroke="#303848" stroke-width="1.6" stroke-linecap="round"/><line x1="85" y1="43.5" x2="88" y2="41.5" stroke="#303848" stroke-width="1.6" stroke-linecap="round"/><line x1="69" y1="43.5" x2="71" y2="43.5" stroke="#303848" stroke-width="1.6"/>`,
  ribbon:   `<path d="M83 20 Q89 14 92 21 Q89 28 83 22Z" fill="#ff4090"/><path d="M101 20 Q95 14 92 21 Q95 28 101 22Z" fill="#ff4090"/><circle cx="92" cy="21" r="4" fill="#ff80b8"/>`,
  bowtie:   `<path d="M55 62 Q62 56 69 62 Q62 68 55 62Z" fill="#2855cc"/><path d="M71 62 Q78 56 85 62 Q78 68 71 62Z" fill="#2855cc"/><circle cx="70" cy="62" r="4" fill="#3a68e0"/>`,
  necklace: `<path d="M49 58 Q70 70 91 58" stroke="#d4ae28" stroke-width="2.4" fill="none" stroke-linecap="round"/><ellipse cx="70" cy="69" rx="5" ry="4" fill="#e8c838"/><ellipse cx="70" cy="69" rx="3" ry="2.5" fill="#c8a018"/>`,
};

const AV_CAT_EXPR = {
  happy:   `<ellipse cx="63" cy="44" rx="5.8" ry="7" fill="#120a02"/><ellipse cx="77" cy="44" rx="5.8" ry="7" fill="#120a02"/><ellipse cx="63" cy="44" rx="4.2" ry="6" fill="#3c1e06"/><ellipse cx="77" cy="44" rx="4.2" ry="6" fill="#3c1e06"/><ellipse cx="63" cy="44" rx="2" ry="5.5" fill="#0a0402"/><ellipse cx="77" cy="44" rx="2" ry="5.5" fill="#0a0402"/><circle cx="65.5" cy="40.5" r="2.6" fill="white"/><circle cx="79.5" cy="40.5" r="2.6" fill="white"/><circle cx="60.5" cy="47" r="1.3" fill="white" opacity="0.55"/><circle cx="74.5" cy="47" r="1.3" fill="white" opacity="0.55"/>`,
  focused: `<ellipse cx="63" cy="45" rx="5.8" ry="5" fill="#120a02"/><ellipse cx="77" cy="45" rx="5.8" ry="5" fill="#120a02"/><ellipse cx="63" cy="45" rx="4.2" ry="4" fill="#3c1e06"/><ellipse cx="77" cy="45" rx="4.2" ry="4" fill="#3c1e06"/><ellipse cx="63" cy="45" rx="2" ry="3.5" fill="#0a0402"/><ellipse cx="77" cy="45" rx="2" ry="3.5" fill="#0a0402"/><circle cx="65" cy="42" r="2" fill="white"/><circle cx="79" cy="42" r="2" fill="white"/><path d="M57 39 L69 42" stroke="#4a2808" stroke-width="2.2" stroke-linecap="round"/><path d="M71 42 L83 39" stroke="#4a2808" stroke-width="2.2" stroke-linecap="round"/>`,
  wink:    `<ellipse cx="63" cy="44" rx="5.8" ry="7" fill="#120a02"/><ellipse cx="63" cy="44" rx="4.2" ry="6" fill="#3c1e06"/><ellipse cx="63" cy="44" rx="2" ry="5.5" fill="#0a0402"/><circle cx="65.5" cy="40.5" r="2.6" fill="white"/><circle cx="60.5" cy="47" r="1.3" fill="white" opacity="0.55"/><path d="M71 44 Q77 51.5 83 44" stroke="#120a02" stroke-width="3.4" fill="none" stroke-linecap="round"/>`,
  sleepy:  `<path d="M57 46 Q63 38 69 46" fill="#120a02"/><path d="M71 46 Q77 38 83 46" fill="#120a02"/><path d="M58 46 Q63 40.5 68 46 Q63 42 58 46Z" fill="#3c1e06"/><path d="M72 46 Q77 40.5 82 46 Q77 42 72 46Z" fill="#3c1e06"/><circle cx="65" cy="43" r="1.8" fill="white" opacity="0.7"/><circle cx="79" cy="43" r="1.8" fill="white" opacity="0.7"/>`,
};

const AV_BICHON_EXPR = {
  happy:   `<circle cx="63" cy="44" r="6.5" fill="#1a1008"/><circle cx="77" cy="44" r="6.5" fill="#1a1008"/><circle cx="65.5" cy="41" r="2.8" fill="white"/><circle cx="79.5" cy="41" r="2.8" fill="white"/><circle cx="60.5" cy="47" r="1.4" fill="white" opacity="0.5"/><circle cx="74.5" cy="47" r="1.4" fill="white" opacity="0.5"/>`,
  focused: `<circle cx="63" cy="44" r="6.5" fill="#1a1008"/><circle cx="77" cy="44" r="6.5" fill="#1a1008"/><path d="M56 38 Q63 36 70 38" stroke="#4a2808" stroke-width="2.2" stroke-linecap="round" fill="none"/><path d="M70 38 Q77 36 84 38" stroke="#4a2808" stroke-width="2.2" stroke-linecap="round" fill="none"/><circle cx="65" cy="43" r="2.5" fill="white"/><circle cx="79" cy="43" r="2.5" fill="white"/>`,
  wink:    `<circle cx="63" cy="44" r="6.5" fill="#1a1008"/><circle cx="65.5" cy="41" r="2.8" fill="white"/><path d="M71 44 Q77 51.5 83 44" stroke="#1a1008" stroke-width="3.4" fill="none" stroke-linecap="round"/>`,
  sleepy:  `<path d="M56.5 47 Q63 38 69.5 47" fill="#1a1008"/><path d="M70.5 47 Q77 38 83.5 47" fill="#1a1008"/><path d="M57.5 47 Q63 41.5 68.5 47 Q63 43.5 57.5 47Z" fill="#383020"/><path d="M71.5 47 Q77 41.5 82.5 47 Q77 43.5 71.5 47Z" fill="#383020"/><circle cx="64" cy="44" r="1.8" fill="white" opacity="0.7"/><circle cx="78" cy="44" r="1.8" fill="white" opacity="0.7"/>`,
};

const AV_OUTFIT_SVG = {
  none:   '',
  hoodie: `<path d="M30 107 Q31 80 70 78 Q109 80 110 107Z" fill="#3060e0"/><path d="M51 78 Q44 70 42 63" stroke="#2850d0" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M89 78 Q96 70 98 63" stroke="#2850d0" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M57 92 Q70 90 83 92 Q83 102 70 102 Q57 102 57 92Z" fill="#2850d0"/>`,
  knit:   `<path d="M31 107 Q31 80 70 78 Q109 80 109 107Z" fill="#c83060"/><path d="M36 87 Q53 83 70 87 Q87 83 104 87" stroke="rgba(255,255,255,0.2)" stroke-width="2.5" fill="none"/><path d="M35 93 Q53 89 70 93 Q87 89 105 93" stroke="rgba(255,255,255,0.2)" stroke-width="2.5" fill="none"/><path d="M35 99 Q53 95 70 99 Q87 95 105 99" stroke="rgba(255,255,255,0.2)" stroke-width="2.5" fill="none"/>`,
  cape:   `<path d="M35 68 Q29 84 34 108 Q70 116 106 108 Q111 84 105 68 Q88 73 70 73 Q52 73 35 68Z" fill="#6010a0" opacity="0.9"/><path d="M35 68 Q27 86 31 108 Q39 102 47 97 Q41 82 44 70Z" fill="#5008c0" opacity="0.75"/><path d="M50 68 Q70 62 90 68" stroke="rgba(180,80,255,0.35)" stroke-width="3" fill="none" stroke-linecap="round"/>`,
  formal: `<path d="M32 107 Q32 80 70 78 Q108 80 108 107Z" fill="#1a2040"/><path d="M55 75 L62 83 L70 79 L78 83 L85 75" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M67.5 79 L70 87 L72.5 79 Q70 75 67.5 79Z" fill="#c03030"/><line x1="70" y1="82" x2="70" y2="107" stroke="#2a3050" stroke-width="1.5" stroke-dasharray="3,3"/>`,
  space:  `<path d="M28 107 Q28 76 70 74 Q112 76 112 107Z" fill="#c8d8e8"/><path d="M44 78 Q33 85 30 97" stroke="white" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M96 78 Q107 85 110 97" stroke="white" stroke-width="4" fill="none" stroke-linecap="round"/><rect x="55" y="82" width="30" height="18" rx="4" fill="#a8b8c8"/><circle cx="65" cy="91" r="2.5" fill="#6ee7c0"/><circle cx="70" cy="91" r="2.5" fill="#fbbf24"/><circle cx="75" cy="91" r="2.5" fill="#f06363"/>`,
};

const CHARACTER_CONFIGS = {
  cat: {
    id: 'cat', labelKo: '고양이', emoji: '🐱',
    defaults: { bodyColor:'orange', earColor:'pink', hat:'none', accessory:'none', expression:'happy', outfit:'none' },
    colorGroups: [
      { key:'bodyColor', label:'몸 색상', options:[
        {id:'orange',color:'linear-gradient(135deg,#ffc870,#c07030)',label:'오렌지'},
        {id:'gray',  color:'linear-gradient(135deg,#e0e0f0,#606070)',label:'그레이'},
        {id:'cream', color:'linear-gradient(135deg,#fff8e8,#d0a060)',label:'크림'},
        {id:'brown', color:'linear-gradient(135deg,#c09050,#603010)',label:'브라운'},
        {id:'black', color:'linear-gradient(135deg,#606060,#101018)',label:'블랙'},
        {id:'white', color:'linear-gradient(135deg,#ffffff,#d0d0d8)',label:'화이트',outline:true},
      ]},
      { key:'earColor', label:'귀 속 색상', options:[
        {id:'pink', color:'linear-gradient(135deg,#ffd0dc,#f070a0)',label:'핑크'},
        {id:'mint', color:'linear-gradient(135deg,#c0f0e0,#40c090)',label:'민트'},
        {id:'lilac',color:'linear-gradient(135deg,#e8d0f8,#9060c8)',label:'라일락'},
        {id:'coral',color:'linear-gradient(135deg,#ffd8c0,#f07050)',label:'코랄'},
      ]},
    ],
  },
  bichon: {
    id: 'bichon', labelKo: '비숑', emoji: '🐶',
    defaults: { coatColor:'white', hat:'none', accessory:'none', expression:'happy', outfit:'none' },
    colorGroups: [
      { key:'coatColor', label:'털 색상', options:[
        {id:'white', color:'linear-gradient(135deg,#ffffff,#e8e8f0)',label:'퓨어 화이트',outline:true},
        {id:'cream', color:'linear-gradient(135deg,#fffaf0,#ddd0a0)',label:'크림'},
        {id:'golden',color:'linear-gradient(135deg,#fff8d8,#d0a840)',label:'골든'},
        {id:'silver',color:'linear-gradient(135deg,#edf0f5,#b0b8c8)',label:'실버'},
      ]},
    ],
  },
};

const SHARED_OPTIONS = [
  { key:'hat', label:'모자', options:[
    {id:'none',emoji:'—',label:'없음'},{id:'party',emoji:'🎉',label:'파티'},
    {id:'wizard',emoji:'🧙',label:'마법사'},{id:'crown',emoji:'👑',label:'왕관'},
    {id:'santa',emoji:'🎅',label:'산타'},{id:'beanie',emoji:'🧢',label:'비니'},
    {id:'beret',emoji:'🎩',label:'베레모'},
  ]},
  { key:'outfit', label:'옷', options:[
    {id:'none',emoji:'—',label:'없음'},{id:'hoodie',emoji:'👕',label:'후드티'},
    {id:'knit',emoji:'🧶',label:'니트'},{id:'cape',emoji:'🦸',label:'망토'},
    {id:'formal',emoji:'👔',label:'교복'},{id:'space',emoji:'🚀',label:'우주복'},
  ]},
  { key:'accessory', label:'악세서리', options:[
    {id:'none',emoji:'—',label:'없음'},{id:'glasses',emoji:'👓',label:'안경'},
    {id:'ribbon',emoji:'🎀',label:'리본'},{id:'bowtie',emoji:'🪢',label:'나비넥타이'},
    {id:'necklace',emoji:'📿',label:'목걸이'},
  ]},
  { key:'expression', label:'표정', options:[
    {id:'happy',emoji:'😊',label:'행복'},{id:'focused',emoji:'😤',label:'집중'},
    {id:'wink',emoji:'😉',label:'윙크'},{id:'sleepy',emoji:'😴',label:'졸린'},
  ]},
];

const AV_TAB_POS = {
  gc: { cx:83, cy:36, r:23, bodyCx:83, bodyCy:78, bodyRx:28, bodyRy:13, hatTx:23.4, hatTy:-2.3, hatS:0.852, ex1:78, ey1:35, ex2:88, ey2:35, rY:5.8 },
  sc: { cx:49, cy:34, r:21, bodyCx:49, bodyCy:78, bodyRx:22, bodyRy:12, hatTx:-5.5, hatTy:-1,   hatS:0.778, ex1:44, ey1:33, ex2:54, ey2:33, rY:5.5 },
  wc: { cx:65, cy:30, r:21, bodyCx:65, bodyCy:53, bodyRx:24, bodyRy:9,  hatTx:10.5, hatTy:-5,   hatS:0.778, ex1:60, ey1:29, ex2:70, ey2:29, rY:5.5 },
  rc: { cx:65, cy:38, r:21, bodyCx:65, bodyCy:50, bodyRx:24, bodyRy:9,  hatTx:10.5, hatTy:3,    hatS:0.778, ex1:60, ey1:37, ex2:70, ey2:37, rY:4.5 },
  ec: { cx:58, cy:36, r:21, bodyCx:58, bodyCy:78, bodyRx:26, bodyRy:13, hatTx:3.5,  hatTy:1,    hatS:0.778, ex1:53, ey1:35, ex2:63, ey2:35, rY:5.5 },
  cc: { cx:65, cy:38, r:22, bodyCx:65, bodyCy:80, bodyRx:26, bodyRy:12, hatTx:8,    hatTy:1.3,  hatS:0.815, ex1:62, ey1:38, ex2:68, ey2:38, rY:5.5 },
  mc: { cx:65, cy:32, r:22, bodyCx:65, bodyCy:62, bodyRx:25, bodyRy:11, hatTx:8,    hatTy:-4.7, hatS:0.815, ex1:60, ey1:32, ex2:70, ey2:32, rY:5.5 },
};

const AvatarSystem = (() => {
  const KEY = 'avatarState_v2';

  function _defaults() {
    const s = { selectedCharacter: 'cat', customization: {} };
    Object.keys(CHARACTER_CONFIGS).forEach(id => {
      s.customization[id] = { ...CHARACTER_CONFIGS[id].defaults };
    });
    return s;
  }

  let _state = _defaults();

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) {
        const old = JSON.parse(localStorage.getItem('catConfig') || 'null');
        if (old) {
          _state.customization.cat = {
            bodyColor: old.bodyColor || 'orange',
            earColor:  old.earColor  || 'pink',
            hat:       old.hat       || 'none',
            accessory: old.accessory || 'none',
            expression:old.expression|| 'happy',
            outfit:    'none',
          };
        }
        return;
      }
      const saved = JSON.parse(raw);
      if (saved.selectedCharacter && CHARACTER_CONFIGS[saved.selectedCharacter]) {
        _state.selectedCharacter = saved.selectedCharacter;
      }
      if (saved.customization) {
        Object.keys(CHARACTER_CONFIGS).forEach(id => {
          if (saved.customization[id]) {
            _state.customization[id] = { ...CHARACTER_CONFIGS[id].defaults, ...saved.customization[id] };
          }
        });
      }
    } catch (e) {}
  }

  function save() {
    localStorage.setItem(KEY, JSON.stringify(_state));
  }

  function get() { return _state; }

  function setCharacter(charId) {
    if (!CHARACTER_CONFIGS[charId]) return;
    _state.selectedCharacter = charId;
    save();
    AvatarRenderer.applyAll(_state);
    if (typeof AvatarCustomizer !== 'undefined') AvatarCustomizer.refresh();
  }

  function setOption(key, val) {
    _state.customization[_state.selectedCharacter][key] = val;
    save();
    AvatarRenderer.applyAll(_state);
    if (typeof AvatarCustomizer !== 'undefined') AvatarCustomizer.refreshPreview();
  }

  return { load, save, get, setCharacter, setOption };
})();
