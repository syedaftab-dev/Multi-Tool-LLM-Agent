/**
 * config.js
 * ---------
 * All detection signatures live here, separate from logic (detection.js) and
 * UI (popup.js). This is intentional: FlexyPe's actual script/CDN naming
 * conventions weren't available to test against during this assignment, so
 * every signal is written as a *pattern family* (naming variants, common
 * abbreviations, likely CDN hosts) rather than one hardcoded string. Real
 * Shopify apps are consistent about a few things regardless of exact naming:
 * a dedicated script host, a global namespace object, and a DOM
 * root/container for their widget. We detect against all three, plus
 * comments/hidden nodes for the "disabled" case.
 *
 * To extend: add/edit patterns here. No changes to detection.js needed.
 */

const FLEXYPE_SIGNAL_CONFIG = {
  "FlexyPe Checkout": {
    // matched against script src / resource URLs
    scriptPatterns: [
      /flexype[-_]?checkout/i,
      /checkout[.\-_]flexype/i,
      /fp[-_]checkout/i,
      /flexype\.io\/checkout/i
    ],
    // matched against window.* keys present on the page
    globalVars: ["FlexyPeCheckout", "FlexyCheckout", "__FLEXYPE_CHECKOUT__", "flexypeCheckout", "FPCheckout"],
    // matched against element selectors actually present in the DOM
    domSelectors: [
      "[data-flexype-checkout]", "[data-fp-checkout]",
      ".flexype-checkout", ".flexy-checkout-widget",
      "#flexype-checkout-root", "#fp-checkout-container",
      "[id*='flexype-checkout']", "[class*='flexype-checkout']",
      "[id*='flexy-checkout']", "[class*='flexy-checkout']"
    ],
    // loose text signals — weak on their own, used for comment/disabled scan
    keywordHints: ["flexype checkout", "flexy checkout", "flexypecheckout", "fp-checkout"]
  },

  "FlexyPass": {
    scriptPatterns: [
      /flexy[-_]?pass/i,
      /fp[-_]pass/i,
      /flexype\.io\/pass/i,
      // CONFIRMED real filename on zouraofficial.com: "pass.min.js" — loaded
      // alongside flexype-v2.min.js (the confirmed FlexyPe core). The name
      // alone is generic/ambiguous (any site could have an unrelated
      // pass.min.js), so this is intentionally the lowest-confidence entry
      // here; the platform-host co-occurrence is what actually makes it
      // trustworthy in practice, not this pattern in isolation.
      /(^|\/)pass\.min\.js(\?|$)/i
    ],
    globalVars: ["FlexyPass", "__FLEXYPASS__", "flexyPass", "FPPass"],
    domSelectors: [
      "[data-flexypass]", "[data-fp-pass]",
      ".flexypass-widget", ".flexy-pass-badge",
      "#flexypass-container", "#fp-pass-root",
      "[id*='flexypass']", "[class*='flexypass']",
      "[id*='flexy-pass']", "[class*='flexy-pass']"
    ],
    keywordHints: ["flexypass", "flexy pass", "fp-pass"]
  },

  "FlexyCart": {
    scriptPatterns: [
      /flexype[-_]?cart/i,   // CONFIRMED real: flexype-cart-entry.min.js, flexype-cart-app.min.js (zouraofficial.com)
      /flexy[-_]?cart/i,
      /fp[-_]cart/i,
      /flexype\.io\/cart/i
    ],
    globalVars: ["FlexyCart", "__FLEXYCART__", "flexyCart", "FPCart"],
    domSelectors: [
      "[data-flexycart]", "[data-fp-cart]",
      ".flexycart-drawer", ".flexy-cart-widget",
      "#flexycart-root", "#fp-cart-container",
      "[id*='flexycart']", "[class*='flexycart']",
      "[id*='flexy-cart']", "[class*='flexy-cart']"
    ],
    keywordHints: ["flexycart", "flexy cart", "fp-cart", "flexype-cart"]
  }
};

// Generic FlexyPe platform CDN/host patterns — a match here doesn't identify
// *which* product, but raises confidence that FlexyPe is present at all,
// and is shown as supporting evidence for whichever product also scores.
const FLEXYPE_PLATFORM_PATTERNS = [
  /cdn\.flexype\.(io|com)/i,
  /assets\.flexype\.(io|com)/i,
  /js\.flexype\.(io|com)/i,
  /flexype\.io\/(sdk|widget|loader)/i,
  /flexypeapp/i,
  /flexype-v2(\.min)?\.js/i // CONFIRMED real: shared FlexyPe core loader (zouraofficial.com)
];

// Confidence scoring weights — tuned so a single strong signal (a real global
// object actually present on the live page) is enough to call it Detected,
// while scattered weak text/keyword mentions alone land in "Likely".
const SIGNAL_WEIGHTS = {
  globalVar: 40,
  scriptPattern: 30,
  domSelector: 25,
  platformHost: 15,
  keywordHint: 10
};

const CONFIDENCE_THRESHOLDS = {
  detected: 40,
  likely: 15
};

// Small reference DB of well-known Shopify ecosystem apps, matched by the
// CDN/host their loader scripts come from. This powers Part 1's "third-party
// apps present" ask using the same resource-URL signal the FlexyPe detector
// already collects — no extra page cost.
const KNOWN_APP_HOST_PATTERNS = [
  { name: "Klaviyo", pattern: /klaviyo\.com/i, category: "Email/SMS marketing" },
  { name: "Yotpo", pattern: /yotpo\.com/i, category: "Reviews" },
  { name: "Judge.me", pattern: /judge\.me/i, category: "Reviews" },
  { name: "Loox", pattern: /loox\.(io|com)/i, category: "Reviews" },
  { name: "Stamped.io", pattern: /stamped\.io/i, category: "Reviews" },
  { name: "ReviewsIO", pattern: /reviews\.io/i, category: "Reviews" },
  { name: "Recharge", pattern: /rechargeapps\.com|rechargepayments\.com/i, category: "Subscriptions" },
  { name: "Bold Subscriptions", pattern: /boldapps\.net/i, category: "Subscriptions" },
  { name: "Gorgias", pattern: /gorgias\.(chat|com)/i, category: "Helpdesk/Chat" },
  { name: "Tidio", pattern: /tidio\.co/i, category: "Chat" },
  { name: "PageFly", pattern: /pagefly\.io/i, category: "Page builder" },
  { name: "Shogun", pattern: /getshogun\.com/i, category: "Page builder" },
  { name: "Zipify", pattern: /zipify\.com/i, category: "Upsell/Funnel" },
  { name: "Rebuy", pattern: /rebuyengine\.com/i, category: "Upsell/Personalization" },
  { name: "Vitals", pattern: /vitals\.co/i, category: "All-in-one apps" },
  { name: "Privy", pattern: /privy\.com/i, category: "Popups/Email capture" },
  { name: "Justuno", pattern: /justuno\.com/i, category: "Popups/CRO" },
  { name: "Smile.io", pattern: /smile\.io/i, category: "Loyalty/Rewards" },
  { name: "Swym", pattern: /swymrelay\.com/i, category: "Wishlist" },
  { name: "AfterShip", pattern: /aftership\.com/i, category: "Order tracking" },
  { name: "Attentive", pattern: /attentivemobile\.com/i, category: "SMS marketing" },
  { name: "Tapcart", pattern: /tapcart\.com/i, category: "Mobile app" },
  { name: "Route", pattern: /(^|\.)route\.com/i, category: "Shipping protection" },
  { name: "Fera", pattern: /fera\.ai/i, category: "Reviews" }
];

// Kept on window for popup.js / detection.js to consume without imports
// (kept as plain scripts to avoid MV3 module-loading/CSP friction in a
// small popup context).
window.FLEXYPE_SIGNAL_CONFIG = FLEXYPE_SIGNAL_CONFIG;
window.FLEXYPE_PLATFORM_PATTERNS = FLEXYPE_PLATFORM_PATTERNS;
window.SIGNAL_WEIGHTS = SIGNAL_WEIGHTS;
window.CONFIDENCE_THRESHOLDS = CONFIDENCE_THRESHOLDS;
window.KNOWN_APP_HOST_PATTERNS = KNOWN_APP_HOST_PATTERNS;
