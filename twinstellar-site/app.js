/* =========================================================
   Twinstellar — MVP engine
   - 五行 from birth-year heavenly stem
   - 星座 from birth month/day
   - lookup one of 60 sacred combinations
   Fully client-side. No backend required.
   ========================================================= */

// ---- Element config (五行) ----
const ELEMENTS = {
  wood:  { name: 'WOOD',  cn: '木', symbol: '🌳', color: '#5DA271', key: 'Expansion · Renewal · Creativity' },
  fire:  { name: 'FIRE',  cn: '火', symbol: '🔥', color: '#E8663B', key: 'Will · Courage · Initiation' },
  earth: { name: 'EARTH', cn: '土', symbol: '🌍', color: '#C9A24B', key: 'Grounding · Patience · Creation' },
  metal: { name: 'METAL', cn: '金', symbol: '⚪', color: '#C7CBD1', key: 'Structure · Mastery · Refinement' },
  water: { name: 'WATER', cn: '水', symbol: '💧', color: '#4F86C6', key: 'Depth · Sensitivity · Dreams' },
};

// ---- Zodiac config (星座) ----
const ZODIAC = {
  aries:      { name: 'ARIES',      cn: '白羊座', symbol: '♈', arche: 'THE PIONEER' },
  taurus:     { name: 'TAURUS',     cn: '金牛座', symbol: '♉', arche: 'THE BUILDER' },
  gemini:     { name: 'GEMINI',     cn: '双子座', symbol: '♊', arche: 'THE MESSENGER' },
  cancer:     { name: 'CANCER',     cn: '巨蟹座', symbol: '♋', arche: 'THE GUARDIAN' },
  leo:        { name: 'LEO',        cn: '狮子座', symbol: '♌', arche: 'THE SOVEREIGN' },
  virgo:      { name: 'VIRGO',      cn: '处女座', symbol: '♍', arche: 'THE PURIFIER' },
  libra:      { name: 'LIBRA',      cn: '天秤座', symbol: '♎', arche: 'THE HARMONIZER' },
  scorpio:    { name: 'SCORPIO',    cn: '天蝎座', symbol: '♏', arche: 'THE PHOENIX' },
  sagittarius:{ name: 'SAGITTARIUS',cn: '射手座', symbol: '♐', arche: 'THE SEEKER' },
  capricorn:  { name: 'CAPRICORN',  cn: '摩羯座', symbol: '♑', arche: 'THE ARCHITECT' },
  aquarius:   { name: 'AQUARIUS',   cn: '水瓶座', symbol: '♒', arche: 'THE VISIONARY' },
  pisces:     { name: 'PISCES',     cn: '双鱼座', symbol: '♓', arche: 'THE MYSTIC' },
};

// ---- Zodiac boundaries (month, day) — checked from late to early ----
const BOUNDARIES = [
  { m: 1,  d: 20, z: 'aquarius' },
  { m: 2,  d: 19, z: 'pisces' },
  { m: 3,  d: 21, z: 'aries' },
  { m: 4,  d: 20, z: 'taurus' },
  { m: 5,  d: 21, z: 'gemini' },
  { m: 6,  d: 21, z: 'cancer' },
  { m: 7,  d: 23, z: 'leo' },
  { m: 8,  d: 23, z: 'virgo' },
  { m: 9,  d: 23, z: 'libra' },
  { m: 10, d: 23, z: 'scorpio' },
  { m: 11, d: 22, z: 'sagittarius' },
  { m: 12, d: 22, z: 'capricorn' },
];

// ---- Material tiers (configurable prices) ----
const TIERS = [
  { id: 'steel',  name: 'Surgical Steel', desc: 'Everyday · Hypoallergenic', price: 88 },
  { id: 'silver', name: 'Sterling Silver', desc: 'Classic · Hand-finished',  price: 128 },
  { id: 'gold',   name: '18K Gold Finish', desc: 'Premium · Limited',         price: 168 },
];

// ---- CHECKOUT: drop in your Stripe / Shopify / checkout link here ----
// Leave as '' to use the built-in pre-order email capture.
const CHECKOUT_BASE = '';

// ---------- calculations ----------
function calculateElement(year) {
  const stem = (year - 4) % 10;
  const order = ['wood', 'fire', 'earth', 'metal', 'water'];
  return order[Math.floor(stem / 2)];
}

function calculateZodiac(month, day) {
  for (const b of BOUNDARIES.slice().reverse()) {
    if (month > b.m || (month === b.m && day >= b.day)) return b.z;
  }
  return 'capricorn';
}

function findCombo(element, zodiac) {
  const list = window.TWIN_COMBOS || [];
  return list.find(c => c.element.toLowerCase() === element && c.zodiac.toLowerCase() === zodiac) || null;
}

// ---------- rendering ----------
const $ = (id) => document.getElementById(id);

function renderResult(name, combo) {
  const el = ELEMENTS[combo.element.toLowerCase()];
  const zx = ZODIAC[combo.zodiac.toLowerCase()];

  $('resultName').textContent = name ? `${name}, this is you.` : 'This is you.';

  // element
  $('elementCard').style.setProperty('--el-color', el.color);
  $('elementSymbol').textContent = el.symbol;
  $('elementName').textContent = el.name;
  $('elementKey').textContent = el.key;

  // zodiac
  $('zodiacCard').style.setProperty('--zx-color', zx ? '#C9A962' : 'var(--gold)');
  $('zodiacSymbol').textContent = zx.symbol;
  $('zodiacName').textContent = zx.name;
  $('zodiacKey').textContent = zx.arche;

  // title + fusion + mantra
  $('sacredTitleEn').textContent = combo.title_en;
  $('sacredTitleCn').textContent = combo.title_cn;
  $('fusionText').textContent = (combo.fusion || '').replace(/\*\*/g, '');
  $('mantraText').textContent = `“${combo.mantra_en}”`;

  // stones
  $('stonesWrap').innerHTML = (combo.stones || [])
    .map(s => `<span class="stone">${s}</span>`).join('');

  // tiers
  $('tiersWrap').innerHTML = TIERS.map(t => {
    const href = CHECKOUT_BASE
      ? `${CHECKOUT_BASE}?element=${combo.element}&zodiac=${combo.zodiac}&tier=${t.id}`
      : `#claim:${combo.element}-${combo.zodiac}-${t.id}`;
    return `<a class="tier" href="${href}" data-tier="${t.id}">
      <div class="tier-name">${t.name}</div>
      <div class="tier-desc">${t.desc}</div>
      <div class="tier-price">$${t.price}</div>
      <div class="tier-cta">◇ Claim ◇</div>
    </a>`;
  }).join('');

  // wire share + restart
  $('copyLinkBtn').onclick = () => copyLink(name, combo);
  $('restartBtn').onclick = () => { location.hash = '#reveal'; location.reload(); };

  // pre-order capture (when no checkout link configured)
  document.querySelectorAll('.tier').forEach(a => {
    a.addEventListener('click', (e) => {
      if (!CHECKOUT_BASE && a.getAttribute('href').startsWith('#claim')) {
        e.preventDefault();
        preorderCapture(name, combo, a.dataset.tier);
      }
    });
  });
}

function copyLink(name, combo) {
  const url = `${location.origin}${location.pathname}?n=${encodeURIComponent(name || '')}&e=${combo.element}&z=${combo.zodiac}`;
  navigator.clipboard?.writeText(url).then(() => {
    $('copyLinkBtn').textContent = 'Link copied ✓';
    setTimeout(() => ($('copyLinkBtn').textContent = 'Copy my universe link'), 2000);
  });
}

function preorderCapture(name, combo, tierId) {
  const tier = TIERS.find(t => t.id === tierId);
  const subject = `Claim ${combo.title_en} (${tier.name})`;
  const body = `Hi Twinstellar,%0D%0A%0D%0AI'd like to claim my sacred bracelet:%0D%0AName: ${encodeURIComponent(name || '—')}%0D%0ACombination: ${combo.title_en} (${combo.element} + ${combo.zodiac})%0D%0AMaterial: ${tier.name}%0D%0A%0D%0AThank you!`;
  // store intent locally (for later automation / retargeting)
  try {
    const leads = JSON.parse(localStorage.getItem('twin_leads') || '[]');
    leads.push({ name, element: combo.element, zodiac: combo.zodiac, tier: tierId, ts: Date.now() });
    localStorage.setItem('twin_leads', JSON.stringify(leads));
  } catch (_) {}
  window.location.href = `mailto:hello@twinstellar.com?subject=${encodeURIComponent(subject)}&body=${body}`;
}

// ---------- flow ----------
function show(view) {
  ['home', 'reveal', 'loading', 'result', 'story'].forEach(id => {
    const el = $(id);
    if (el) el.hidden = (id !== view);
  });
  if (view !== 'result') window.scrollTo({ top: 0, behavior: 'smooth' });
}

function runReveal(name, dateStr) {
  const date = new Date(dateStr + 'T00:00:00');
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const element = calculateElement(year);
  const zodiac = calculateZodiac(month, day);
  const combo = findCombo(element, zodiac);
  if (!combo) { alert('Something went wrong reading the stars. Please try again.'); return; }

  show('loading');
  window.scrollTo({ top: 0, behavior: 'smooth' });
  setTimeout(() => {
    renderResult(name, combo);
    show('result');
    // deep link support
    history.replaceState(null, '', `?n=${encodeURIComponent(name)}&e=${element}&z=${zodiac}`);
  }, 2600);
}

// ---------- init ----------
document.addEventListener('DOMContentLoaded', () => {
  // starfield
  initStars();

  $('revealForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const name = $('nameInput').value.trim();
    const birth = $('birthInput').value;
    if (!name || !birth) {
      $('formError').hidden = false;
      return;
    }
    $('formError').hidden = true;
    runReveal(name, birth);
  });

  // deep-link: ?n=&e=&z= → show result directly
  const params = new URLSearchParams(location.search);
  const e = params.get('e'), z = params.get('z'), n = params.get('n');
  if (e && z) {
    const combo = findCombo(e, z);
    if (combo) { renderResult(n || '', combo); show('result'); return; }
  }
  show('home');
});

// ---------- starfield (lightweight canvas) ----------
function initStars() {
  const c = $('stars');
  const ctx = c.getContext('2d');
  let w, h, stars;
  function resize() {
    w = c.width = window.innerWidth;
    h = c.height = window.innerHeight;
    const n = Math.min(160, Math.floor(w * h / 9000));
    stars = Array.from({ length: n }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 1.3 + 0.2, a: Math.random(), s: Math.random() * 0.02 + 0.004,
    }));
  }
  function tick() {
    ctx.clearRect(0, 0, w, h);
    for (const st of stars) {
      st.a += st.s;
      const tw = 0.5 + 0.5 * Math.sin(st.a);
      ctx.beginPath();
      ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(231,205,149,${tw * 0.8})`;
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }
  resize();
  window.addEventListener('resize', resize);
  tick();
}
