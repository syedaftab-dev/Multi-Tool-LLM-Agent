/**
 * collector.js
 * ------------
 * `collectPageSignals` is handed to chrome.scripting.executeScript as `func`
 * and runs INSIDE the inspected storefront tab, in the page's MAIN world
 * (not the isolated content-script world) — that's the only place
 * `window.Shopify` and any real `window.FlexyPe*` globals actually exist.
 *
 * IMPORTANT SERIALIZATION NOTE: args passed through executeScript are
 * structured-cloned, so RegExp objects do NOT survive as RegExp — they'd
 * arrive as `{}`. Config patterns are therefore passed in as plain
 * {source, flags} strings and reconstructed with `new RegExp(...)` here,
 * inside the page context, where all the actual matching happens. Only
 * plain serializable results are returned back to the popup.
 */

function collectPageSignals(serializedConfig) {
  const toRe = (p) => new RegExp(p.source, p.flags);

  const signals = serializedConfig.signals;
  const platformPatterns = serializedConfig.platformPatterns.map(toRe);
  const appHostPatterns = serializedConfig.appHostPatterns.map((a) => ({ ...a, pattern: toRe(a.pattern) }));

  // ---- Part 1: Store info -------------------------------------------------
  const shopify = window.Shopify || null;
  const storeInfo = {
    storeUrl: location.hostname,
    shopifyDomain: (shopify && (shopify.shop || shopify.domain)) || null,
    shopName: (document.querySelector('meta[property="og:site_name"]') || {}).content || null,
    currency: (shopify && shopify.currency && (shopify.currency.active || shopify.currency)) || null,
    country: (shopify && shopify.country) || null,
    locale: (shopify && shopify.locale) || document.documentElement.lang || null,
    themeName: (shopify && shopify.theme && shopify.theme.name) || null,
    themeId: (shopify && shopify.theme && shopify.theme.id) || null,
    currentPage: (function () {
      const p = location.pathname;
      if (p === "/" || p === "") return "Home";
      if (p.startsWith("/products/")) return "Product";
      if (p.startsWith("/collections/")) return "Collection";
      if (p.startsWith("/cart")) return "Cart";
      if (p.startsWith("/pages/")) return "Page";
      if (p.startsWith("/blogs/")) return "Blog";
      if (p.startsWith("/checkout")) return "Checkout";
      return "Other";
    })(),
    hasShopifyObject: !!shopify,
    poweredByShopify: !!shopify || /cdn\.shopify\.com|myshopify\.com/i.test(document.documentElement.outerHTML.slice(0, 20000))
  };

  // ---- Raw resource / script inventory ------------------------------------
  const resourceUrls = (performance.getEntriesByType("resource") || []).map((r) => r.name);
  const scriptSrcs = Array.from(document.querySelectorAll("script[src]")).map((s) => s.src);
  const allUrls = Array.from(new Set([...resourceUrls, ...scriptSrcs]));

  const inlineScriptText = Array.from(document.querySelectorAll("script:not([src])"))
    .map((s) => s.textContent || "")
    .join("\n")
    .slice(0, 200000);

  // ---- Part 3 raw material: comments anywhere in the DOM ------------------
  const commentTexts = [];
  const walker = document.createTreeWalker(document, NodeFilter.SHOW_COMMENT, null);
  let node;
  while ((node = walker.nextNode())) {
    const text = (node.nodeValue || "").trim();
    if (text.length > 0 && text.length < 4000) commentTexts.push(text);
  }
  const commentBlob = commentTexts.join("\n");

  // ---- Per-product signal evaluation --------------------------------------
  const productResults = {};
  Object.keys(signals).forEach((product) => {
    const cfg = signals[product];
    const scriptPatterns = cfg.scriptPatterns.map(toRe);

    const matchedUrls = allUrls.filter((u) => scriptPatterns.some((re) => re.test(u)));
    const matchedGlobals = cfg.globalVars.filter((name) => typeof window[name] !== "undefined");

    // A real integration global often carries its own live/disabled flag
    // (e.g. { active: true, ready: true }). Read it when present instead of
    // treating "the object exists" as automatically meaning "live" — a
    // FlexyPe object with active:false is the strongest possible evidence
    // for Part 3, stronger than any comment/hidden-node guess.
    const globalStates = matchedGlobals.map((name) => {
      const obj = window[name];
      const state = {};
      if (obj && typeof obj === "object") {
        if (typeof obj.active === "boolean") state.active = obj.active;
        if (typeof obj.ready === "boolean") state.ready = obj.ready;
        if (typeof obj.region === "string") state.region = obj.region;
        if (obj.region && typeof obj.region === "object" && obj.region.country_name) state.country = obj.region.country_name;
        if (typeof obj.mid === "string") state.merchantId = obj.mid;
        if (obj.config && typeof obj.config.env === "string") state.env = obj.config.env;
      }
      return { name, state };
    });
    const anyGlobalExplicitlyInactive = globalStates.some((g) => g.state.active === false);
    const anyGlobalExplicitlyActive = globalStates.some((g) => g.state.active === true);

    const matchedDom = cfg.domSelectors.filter((sel) => {
      try {
        return document.querySelector(sel) !== null;
      } catch (e) {
        return false;
      }
    });

    const matchedKeywordsLive =
      cfg.keywordHints.some((kw) => inlineScriptText.toLowerCase().includes(kw.toLowerCase())) || matchedDom.length > 0;

    const matchedKeywordsInComments = cfg.keywordHints.filter((kw) => commentBlob.toLowerCase().includes(kw.toLowerCase()));

    let hiddenNodesForProduct = [];
    try {
      const sel = cfg.domSelectors.join(",");
      hiddenNodesForProduct = Array.from(document.querySelectorAll(sel))
        .filter((el) => {
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          return style.display === "none" || style.visibility === "hidden" || el.hidden === true || (rect.width === 0 && rect.height === 0);
        })
        .map((el) => ({ tag: el.tagName.toLowerCase(), id: el.id || null, className: el.className || null, snippet: el.outerHTML.slice(0, 300) }));
    } catch (e) {
      hiddenNodesForProduct = [];
    }

    const platformHostMatch = allUrls.some((u) => platformPatterns.some((re) => re.test(u)));

    productResults[product] = {
      matchedUrls,
      matchedGlobals,
      globalStates,
      anyGlobalExplicitlyInactive,
      anyGlobalExplicitlyActive,
      matchedDom,
      matchedKeywordsLive,
      matchedKeywordsInComments,
      hiddenNodesForProduct,
      platformHostMatch
    };
  });

  // ---- Known third-party app detection (reuses the same URL inventory) ---
  const detectedApps = [];
  appHostPatterns.forEach((app) => {
    const hit = allUrls.find((u) => app.pattern.test(u));
    if (hit) detectedApps.push({ name: app.name, category: app.category, matchedUrl: hit });
  });

  return {
    storeInfo,
    productResults,
    detectedApps,
    commentTextsSample: commentTexts.slice(0, 50),
    totalScriptsScanned: allUrls.length,
    totalCommentsScanned: commentTexts.length
  };
}
