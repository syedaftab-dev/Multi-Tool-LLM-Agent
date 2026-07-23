# FlexyPe Store Diagnostics — Chrome Extension

A Manifest V3 Chrome extension that gives Sales/Support an instant read on any
Shopify storefront: store info, which FlexyPe products are live, which are
disabled/commented out, and which third-party apps are installed — all inside
the extension popup, no backend required.

## Setup

1. Open `chrome://extensions`
2. Enable **Developer mode** (top-right toggle)
3. Click **Load unpacked** → select this project folder
4. Pin the extension, then open any Shopify storefront and click the icon

The popup scans on open. Use the ⟳ button top-right to re-scan after the page
changes (e.g. you navigate to a different page on the same store).

## How it works

```
popup.js  (orchestrator, runs in the popup)
  │
  ├─ chrome.scripting.executeScript(world: "MAIN")
  │     runs collectPageSignals() INSIDE the inspected tab
  │
  ├─ collector.js → collectPageSignals()
  │     reads window.Shopify, script/resource URLs, DOM selectors,
  │     window globals, and HTML comments — all live, in the page's
  │     own execution context
  │
  ├─ detection.js → runDetection()
  │     turns raw signal hits into a confidence tier + evidence list
  │
  └─ config.js
        every pattern used above (script name variants, global var
        names, CSS selectors, known third-party app CDNs) — edit this
        file only to tune detection, no logic changes needed
```

No content script runs persistently on every page load — the whole scan is
triggered on-demand via `activeTab` + `scripting.executeScript` when you open
the popup. That's deliberate: it matches how the tool is actually meant to be
used ("open on any storefront to instantly understand the setup"), and it
avoids the extension doing anything on pages nobody's inspecting.

`world: "MAIN"` matters specifically for Part 1's ask to read
`window.Shopify` — a normal content script runs in an *isolated* JS world
that has its own DOM view but cannot see the page's real global variables.
MAIN-world execution is required to see `window.Shopify`, or any
`window.FlexyPe*` object a real integration would expose.

## Detection approach

**Real DevTools testing on both example stores confirmed a working global-
object convention** (`window.FlexyPeCheckout` with an `.active` flag) and
real script filenames for FlexyCart/FlexyPass — see "What I actually found"
below for specifics. Even so, every detector stays a **pattern family**
rather than one hardcoded string, per the assignment's explicit instruction:
merchants on older integration versions, or products this testing didn't
reach, may use naming this hasn't seen yet.

| Signal type | Weight | Why this weight |
|---|---|---|
| `window.<GlobalVar>` present | 40 | Code from the integration actually executed — strongest possible evidence |
| Script/resource URL match | 30 | The vendor's own script loaded, via `performance.getEntriesByType('resource')` + `<script src>` |
| DOM selector match | 25 | A widget container rendered — could be leftover HTML, so weighted below live code |
| Generic FlexyPe CDN host match | 15 | Confirms FlexyPe is present on the store at all, not which product |
| Product name in inline script text | 10 | Weakest — text mention isn't proof of an active integration |

Scores combine into three tiers: **Detected** (≥40, i.e. at least one strong
signal), **Likely** (15–39, only weak/medium corroborating signals), **Not
Detected** (0). The extension never guesses past what it found — "Not
Detected" is the honest answer when signals don't clear the bar, per the
assignment's instruction.

**Disabled/commented integrations (Part 3):** a `TreeWalker` over
`NodeFilter.SHOW_COMMENT` finds every literal HTML comment on the rendered
page, searched for each product's keyword hints. Separately, elements whose
`id`/`class` match a product's own selectors are checked for
`display:none` / `visibility:hidden` / zero-size / `[hidden]` — these read as
"exists but disabled" rather than "removed." This is only surfaced when the
product ISN'T already scored as live, since something can't be both active
and disabled at once. Matched snippets are shown directly in the "Disabled"
tab, per the bonus ask to explain *why* something is considered disabled.

**Third-party app detection:** reuses the exact same resource-URL inventory
already gathered for FlexyPe detection (no extra page cost) against a small
reference list of ~20 well-known Shopify ecosystem apps (Klaviyo, Yotpo,
Recharge, Gorgias, PageFly, Vitals, etc.), matched by their CDN host.

**Bonus config viewer:** `fetchFlexyPeConfig()` in `popup.js` is a documented
stub for the optional backend task — it calls a plausible
`api.flexype.io/v1/config/:product` endpoint and fails gracefully with a
clear message, since no real credentials/API exist in this environment. The
UI (Config tab) is fully wired up; only the network call is a placeholder.

## What I actually found during live investigation

Before finalizing patterns, I tested against the two example stores in a real
browser (DevTools Console + Network tab) rather than guessing blind:

- **`aseemshakti.com`**: `window.FlexyPeCheckout` is real and confirmed live —
  `{ active: true, ready: true, region: {...}, config: { env: "PRODUCTION", ... }, mid: "<merchant id>" }`.
  The `.active` boolean turned out to be a much stronger signal than "does
  the global exist" — it directly distinguishes an installed-but-disabled
  integration from a genuinely live one, so the detector now reads that flag
  instead of just checking for presence.
- **`zouraofficial.com`**: confirmed the same `FlexyPeCheckout` shape holds
  on a second, independent store — good sign it's a stable convention, not a
  one-off. Network tab (filtered by "flex") turned up the real script names:
  `flexype-v2.min.js` (shared core loader), `flexype-cart-entry.min.js` +
  `flexype-cart-app.min.js` (FlexyCart), and `pass.min.js` (FlexyPass).
- **Caught a bug from this**: my original FlexyCart pattern matched
  `"flexy" + "-cart"`, but the real filename is `"flexype" + "-cart"` — the
  extra `pe` broke the match, so FlexyCart would have silently shown
  "Not Detected" on every real store. Fixed once I had the real filename;
  this is exactly why testing against live stores mattered more than
  guessing patterns from the spec alone.
- **`pass.min.js` is a deliberately weak/ambiguous pattern** in `config.js` —
  the name alone could belong to anything. It's only trustworthy because it
  loads alongside the confirmed `flexype-v2.min.js` core script on a real
  FlexyPe store; I kept the pattern but documented the caveat inline rather
  than pretending it's as reliable as a named global object.
- Hit `net::ERR_BLOCKED_BY_CLIENT` on one pass, traced to a browser ad-block
  extension interfering with the Network tab capture — a reminder that this
  kind of diagnostic tooling needs to account for the Sales/Support user's
  own browser extensions potentially masking real signals, not just the
  merchant's setup.

## Known limitations / what I'd do with more time

- FlexyPass and FlexyCart don't yet have a confirmed *global object* the way
  Checkout does (`window.FlexyPass` / `window.FlexyCart` both returned
  `undefined` even once script/network evidence was solid) — either they
  don't expose one, or it's named differently, or it only initializes after
  a further page state (e.g. actually opening the cart drawer). Worth
  checking with the drawer open rather than just on page load.
- Confidence weights are a reasonable starting point, not calibrated against
  a labeled dataset of many real stores with known FlexyPe installs.
- Cross-origin script *contents* aren't fetched (CORS would block most of
  it anyway) — detection relies on URLs, globals, and DOM, not on reading a
  competitor script's source.

## Files

```
manifest.json         MV3 manifest, activeTab + scripting permissions only
popup/popup.html       Tab structure (Store / Products / Disabled / Apps / Config)
popup/popup.css        Styling
popup/popup.js         Orchestration: inject → score → render
popup/collector.js     Runs inside the inspected tab (MAIN world)
popup/detection.js     Scoring/confidence logic (pure functions, no DOM)
popup/config.js        All detection patterns + known-apps reference list
icons/                 Extension icons
```
