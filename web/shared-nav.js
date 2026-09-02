/* =========================================
   ControlPlane.ai — shared-nav.js
   Injects consistent navbar + sidebar + toast
   into every page.
   ========================================= */

const CP_NAV_HTML = `
<nav class="navbar" id="cp-navbar">
  <div class="nav-left">
    <a href="/" class="brand">
      <span class="brand-icon">🛡️</span>
      ControlPlane<span style="color:var(--blue);font-weight:900;">.ai</span>
    </a>
    <ul class="nav-menu">
      <li class="nav-item">
        <a class="nav-link" href="/">Playground</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/audit.html">Audit</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/calibration.html">Grounding</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/bandit.html">Bandit</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/how-it-works.html">How It Works</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="/scale.html">Scale</a>
      </li>
    </ul>
  </div>
  <div class="nav-right">
    <!-- Model Selector -->
    <div class="model-selector-wrap" id="model-selector-wrap">
      <div class="model-selector" id="model-selector-btn">
        <span class="model-dot" id="model-dot"></span>
        <span id="model-selector-label">llama-3.3-70b</span>
        <span style="color:var(--t3);font-size:10px;">▾</span>
      </div>
      <div class="model-dropdown" id="model-dropdown">
        <div class="dropdown-label">Groq Models</div>
        <div class="model-option active" data-model="llama-3.3-70b-versatile" onclick="selectModel(this)">
          <span class="model-option-icon">🦙</span>
          <div class="model-option-label">
            <div style="font-weight:600;">Llama 3.3 70B</div>
            <div style="font-size:11px;color:var(--t3);">Versatile · Fast</div>
          </div>
          <span class="model-option-badge">Tier 0</span>
        </div>
        <div class="model-option" data-model="llama-3.1-8b-instant" onclick="selectModel(this)">
          <span class="model-option-icon">⚡</span>
          <div class="model-option-label">
            <div style="font-weight:600;">Llama 3.1 8B</div>
            <div style="font-size:11px;color:var(--t3);">Instant · Ultra-low latency</div>
          </div>
          <span class="model-option-badge">Tier 0</span>
        </div>
        <div class="model-option" data-model="mixtral-8x7b-32768" onclick="selectModel(this)">
          <span class="model-option-icon">🌪️</span>
          <div class="model-option-label">
            <div style="font-weight:600;">Mixtral 8x7B</div>
            <div style="font-size:11px;color:var(--t3);">MoE · Long context</div>
          </div>
          <span class="model-option-badge tier1">Tier 1</span>
        </div>
        <div class="model-option" data-model="gemma2-9b-it" onclick="selectModel(this)">
          <span class="model-option-icon">💎</span>
          <div class="model-option-label">
            <div style="font-weight:600;">Gemma 2 9B</div>
            <div style="font-size:11px;color:var(--t3);">Google · Instruction-tuned</div>
          </div>
          <span class="model-option-badge">Tier 0</span>
        </div>
        <div class="dropdown-sep"></div>
        <div class="dropdown-label">Local / Mock</div>
        <div class="model-option" data-model="mock" onclick="selectModel(this)">
          <span class="model-option-icon">🤖</span>
          <div class="model-option-label">
            <div style="font-weight:600;">Mock Responder</div>
            <div style="font-size:11px;color:var(--t3);">Offline · No API key needed</div>
          </div>
          <span class="model-option-badge" style="background:var(--surface-3);color:var(--t3);">Local</span>
        </div>
      </div>
    </div>

    <!-- Gateway Status -->
    <div class="status-pill" id="gateway-status-pill">
      <span class="status-dot"></span>
      <span id="gateway-status-text">Connecting...</span>
    </div>

    <!-- CTA -->
    <a href="/" class="btn-nav-action" id="nav-cta">Test Gateway ⚡</a>
  </div>
</nav>

<!-- Toast -->
<div class="toast" id="toast">
  <span id="toast-icon">✓</span>
  <span id="toast-text">Notification</span>
</div>
`;

// ── INJECT NAVBAR ──────────────────────────────
(function injectNav() {
  const placeholder = document.getElementById('cp-nav-placeholder');
  if (placeholder) {
    placeholder.outerHTML = CP_NAV_HTML;
  } else {
    document.body.insertAdjacentHTML('afterbegin', CP_NAV_HTML);
  }

  // Highlight active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href') || '';
    if (href === '/' && path === '/') link.classList.add('active');
    else if (href !== '/' && path.includes(href.replace('.html',''))) link.classList.add('active');
  });
})();

// ── MODEL STATE ────────────────────────────────
let cpSelectedModel = localStorage.getItem('cp_model') || 'llama-3.3-70b-versatile';

function selectModel(el) {
  cpSelectedModel = el.getAttribute('data-model');
  localStorage.setItem('cp_model', cpSelectedModel);
  document.querySelectorAll('.model-option').forEach(o => o.classList.remove('active'));
  el.classList.add('active');
  const isMock = cpSelectedModel === 'mock';
  const label = el.querySelector('.model-option-label div:first-child').innerText;
  document.getElementById('model-selector-label').innerText = label;
  document.getElementById('model-dot').style.background = isMock ? 'var(--yellow-l)' : 'var(--green-l)';
  cpShowToast('Model: ' + label, '🔄');
}

// Restore saved model
(function restoreModel() {
  const opt = document.querySelector('.model-option[data-model="' + cpSelectedModel + '"]');
  if (opt) {
    document.querySelectorAll('.model-option').forEach(o => o.classList.remove('active'));
    opt.classList.add('active');
    const label = opt.querySelector('.model-option-label div:first-child').innerText;
    document.getElementById('model-selector-label').innerText = label;
    if (cpSelectedModel === 'mock') {
      document.getElementById('model-dot').style.background = 'var(--yellow-l)';
    }
  }
})();

// ── GATEWAY PROBE ──────────────────────────────
async function cpProbeGateway() {
  const pill = document.getElementById('gateway-status-pill');
  const text = document.getElementById('gateway-status-text');
  const dot = pill?.querySelector('.status-dot');
  try {
    const r = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: cpSelectedModel,
        messages: [{ role: 'user', content: 'ping' }],
        cp_profile: 'customer_bot',
        stream: false
      })
    });
    if (r.ok) {
      const data = await r.json();
      const ans = (data.choices?.[0]?.message?.content || '').toLowerCase();
      const isMock = ans.includes('mocked') || ans.includes('groq_api_key');
      if (isMock) {
        if (dot) { dot.style.background = 'var(--yellow-l)'; }
        if (pill) { pill.style.background = 'var(--yellow-bg)'; pill.style.color = 'var(--yellow)'; pill.style.borderColor = 'var(--yellow-bd)'; }
        if (text) text.innerText = 'Mock Mode · No API Key';
      } else {
        if (dot) { dot.style.background = 'var(--green-l)'; }
        if (pill) { pill.style.background = 'var(--green-bg)'; pill.style.color = 'var(--green)'; pill.style.borderColor = 'var(--green-bd)'; }
        if (text) text.innerText = 'Gateway Live · Groq Connected';
      }
    } else { throw new Error('HTTP ' + r.status); }
  } catch (e) {
    if (dot) { dot.style.background = 'var(--red)'; dot.style.animation = 'none'; }
    if (pill) { pill.style.background = 'var(--red-bg)'; pill.style.color = 'var(--red)'; pill.style.borderColor = 'var(--red-bd)'; }
    if (text) text.innerText = 'Gateway Offline';
  }
}

// ── SHARED TOAST ───────────────────────────────
function cpShowToast(msg, icon) {
  const t = document.getElementById('toast');
  const tx = document.getElementById('toast-text');
  const ti = document.getElementById('toast-icon');
  if (!t || !tx) return;
  tx.innerText = msg;
  if (ti && icon) ti.innerText = icon;
  t.style.display = 'flex';
  clearTimeout(t._tmr);
  t._tmr = setTimeout(() => { t.style.display = 'none'; }, 3000);
}

// ── INIT ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(cpProbeGateway, 300);
});

// Export for other scripts to use
window.cpSelectedModel = () => cpSelectedModel;
window.cpShowToast = cpShowToast;
