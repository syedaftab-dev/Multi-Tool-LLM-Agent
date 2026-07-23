/**
 * popup.js
 * --------
 * On open: grab the active tab, inject collectPageSignals() into its MAIN
 * world via chrome.scripting.executeScript (activeTab permission — no
 * persistent content script, no background page needed), score the result
 * with detection.js, and render it. Re-running the scan is a button, not
 * automatic, since the point is "open on any storefront, get an instant read."
 */

let lastReport = null;

function reToPlain(re) {
  return { source: re.source, flags: re.flags };
}

function buildSerializedConfig() {
  const signals = {};
  Object.keys(window.FLEXYPE_SIGNAL_CONFIG).forEach((product) => {
    const cfg = window.FLEXYPE_SIGNAL_CONFIG[product];
    signals[product] = {
      scriptPatterns: cfg.scriptPatterns.map(reToPlain),
      globalVars: cfg.globalVars,
      domSelectors: cfg.domSelectors,
      keywordHints: cfg.keywordHints
    };
  });
  return {
    signals,
    platformPatterns: window.FLEXYPE_PLATFORM_PATTERNS.map(reToPlain),
    appHostPatterns: window.KNOWN_APP_HOST_PATTERNS.map((a) => ({ ...a, pattern: reToPlain(a.pattern) }))
  };
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function runScan() {
  show("#loading");
  hide("#notShopify");
  document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));

  const tab = await getActiveTab();
  if (!tab || !tab.id || !/^https?:/.test(tab.url || "")) {
    hide("#loading");
    show("#notShopify");
    return;
  }

  let injectionResult;
  try {
    [injectionResult] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      world: "MAIN",
      func: collectPageSignals,
      args: [buildSerializedConfig()]
    });
  } catch (err) {
    hide("#loading");
    show("#notShopify");
    document.querySelector("#notShopify p.muted").textContent = "Couldn't scan this tab (" + (err.message || err) + "). Some pages (chrome://, the Web Store) block extensions entirely.";
    return;
  }

  const raw = injectionResult && injectionResult.result;
  if (!raw) {
    hide("#loading");
    show("#notShopify");
    return;
  }

  if (!raw.storeInfo.poweredByShopify) {
    hide("#loading");
    show("#notShopify");
    lastReport = raw;
    return;
  }

  const detectionResults = runDetection(raw);
  lastReport = { ...raw, detectionResults, scannedAt: new Date().toISOString(), url: tab.url };

  hide("#loading");
  renderStore(raw.storeInfo);
  renderProducts(detectionResults);
  renderDisabled(detectionResults);
  renderApps(raw.detectedApps);
  renderConfigButtons(detectionResults, raw.storeInfo.shopifyDomain || raw.storeInfo.storeUrl);
  setActiveTab("store");

  document.querySelector("#scanMeta").textContent = `${raw.totalScriptsScanned} resources · ${raw.totalCommentsScanned} comments scanned`;
}

function show(sel) { document.querySelector(sel).classList.remove("hidden"); }
function hide(sel) { document.querySelector(sel).classList.add("hidden"); }

function esc(str) {
  if (str === null || str === undefined) return "—";
  return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function renderStore(info) {
  const rows = [
    ["Store URL", info.storeUrl],
    ["Shopify Domain", info.shopifyDomain],
    ["Shop Name", info.shopName],
    ["Base Currency", info.currency],
    ["Country", info.country],
    ["Locale", info.locale],
    ["Theme Name", info.themeName ? `${info.themeName}${info.themeId ? " (#" + info.themeId + ")" : ""}` : null],
    ["Current Page", info.currentPage]
  ];
  const panel = document.querySelector("#panel-store");
  panel.innerHTML = rows
    .map(([label, value]) => `<div class="field-row"><span class="field-label">${esc(label)}</span><span class="field-value">${esc(value)}</span></div>`)
    .join("");
}

function badgeClass(confidence) {
  if (confidence === "Detected") return "badge-detected";
  if (confidence === "Likely") return "badge-likely";
  return "badge-not";
}

function renderProducts(results) {
  const panel = document.querySelector("#panel-products");
  panel.innerHTML = Object.values(results)
    .map((r) => {
      const evidenceHtml = r.evidence.length
        ? `<ul class="evidence-list">${r.evidence.map((e) => `<li>${esc(e.type)}: <code>${esc(e.detail)}</code></li>`).join("")}</ul>`
        : `<div class="empty-note">No supporting signals found</div>`;
      return `
      <div class="product-card">
        <div class="product-head">
          <span class="product-name">${esc(r.product)}</span>
          <span class="badge ${badgeClass(r.confidence)}">${esc(r.confidence)}</span>
        </div>
        ${evidenceHtml}
      </div>`;
    })
    .join("");
}

function renderDisabled(results) {
  const panel = document.querySelector("#panel-disabled");
  const flagged = Object.values(results).filter((r) => r.possiblyDisabled);
  if (!flagged.length) {
    panel.innerHTML = `<div class="empty-note">No commented-out or hidden FlexyPe integrations detected.</div>`;
    return;
  }
  panel.innerHTML = flagged
    .map(
      (r) => `
    <div class="disabled-card">
      <div class="product-name">${esc(r.product)} — possibly disabled</div>
      ${r.disabledEvidence
        .map((e) => `<div>${esc(e.type)}<span class="snippet">${esc(e.detail)}</span></div>`)
        .join("")}
    </div>`
    )
    .join("");
}

function renderApps(apps) {
  const panel = document.querySelector("#panel-apps");
  if (!apps.length) {
    panel.innerHTML = `<div class="empty-note">No recognized third-party apps found in loaded resources.</div>`;
    return;
  }
  panel.innerHTML = apps
    .map((a) => `<div class="app-row"><span class="app-name">${esc(a.name)}</span><span class="app-category">${esc(a.category)}</span></div>`)
    .join("");
}

/**
 * BONUS TASK (optional, per assignment): fetch each product's backend
 * configuration. There's no real FlexyPe API to call from this environment,
 * so this is a documented stub — the shape a real implementation would take,
 * wired to the UI, failing gracefully instead of pretending to succeed.
 * Swap the fetch URL/auth for the real FlexyPe config endpoint when available.
 */
async function fetchFlexyPeConfig(product, shopDomain) {
  const endpoint = `https://api.flexype.io/v1/config/${encodeURIComponent(product)}?shop=${encodeURIComponent(shopDomain)}`;
  const res = await fetch(endpoint, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`Config API responded ${res.status}`);
  return res.json();
}

function renderConfigButtons(results, shopDomain) {
  const container = document.querySelector("#configButtons");
  const detectedProducts = Object.values(results).filter((r) => r.confidence !== "Not Detected");
  if (!detectedProducts.length) {
    container.innerHTML = `<div class="empty-note">No detected products to fetch config for.</div>`;
    return;
  }
  container.innerHTML = detectedProducts
    .map((r) => `<button class="footer-btn" style="margin:4px 6px 4px 0" data-product="${esc(r.product)}">${esc(r.product)} config</button>`)
    .join("");
  container.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const out = document.querySelector("#configOutput");
      out.classList.remove("hidden");
      out.textContent = "Fetching…";
      try {
        const data = await fetchFlexyPeConfig(btn.dataset.product, shopDomain);
        out.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        out.textContent = `Could not reach FlexyPe config API (${e.message}).\nThis is expected in this environment — no real backend is wired up. See fetchFlexyPeConfig() in popup.js for the intended real implementation.`;
      }
    });
  });
}

function setActiveTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("hidden", p.id !== `panel-${name}`));
}

document.querySelector("#tabs").addEventListener("click", (e) => {
  const btn = e.target.closest(".tab");
  if (!btn) return;
  setActiveTab(btn.dataset.tab);
});

document.querySelector("#rescanBtn").addEventListener("click", runScan);

document.querySelector("#copyReportBtn").addEventListener("click", async () => {
  if (!lastReport) return;
  try {
    await navigator.clipboard.writeText(JSON.stringify(lastReport, null, 2));
    const btn = document.querySelector("#copyReportBtn");
    const original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => (btn.textContent = original), 1200);
  } catch (e) {
    console.error("Clipboard write failed", e);
  }
});

runScan();
