/**
 * detection.js
 * ------------
 * Pure scoring layer. Takes the raw per-product signal hits that
 * collector.js already computed inside the page, and turns them into a
 * confidence tier + a human-readable evidence list. No DOM/page access
 * happens here — this runs in the popup, purely on the returned data, so
 * it's easy to unit-test or tune weights without touching the page-context
 * code at all.
 */

function scoreProduct(productName, raw, weights, thresholds) {
  let evidence = [] ;
  let score = 0

  if(raw.matchedGlobals.length){
    if (raw.anyGlobalExplicitlyActive){
      score += weights.globalVar
      const g = raw.globalStates.find(s => s.state.active === true)
      let extras = [];
      if(g.state.env) extras.push(`env: ${g.state.env}`);
      if (g.state.country) extras.push(`region: ${g.state.country}`) ;
      if(g.state.merchantId) extras.push(`merchant ID: ${g.state.merchantId}`)
      
      const suffix = extras.length ? ` (${extras.join(", ")})` : "";
      evidence.push({ type: "Global object (active)", detail: `window.${g.name}.active === true${suffix}`, strength: "strong" });
    } 
    else if (raw.anyGlobalExplicitlyInactive) {
      // Object exists but explicitly flagged inactive — count it as
      // installed-but-disabled rather than live. Small score bump only
      // (installed, not running) so it lands in "Likely" not "Detected".
      score += weights.keywordHint;
      const g = raw.globalStates.find((s) => s.state.active === false);
      evidence.push({ type: "Global object (inactive)", detail: `window.${g.name}.active === false`, strength: "medium" });
    } else {
      // Object exists with no active/inactive flag exposed — presence alone
      // is still meaningful, just not as conclusive as a confirmed flag.
      score += weights.globalVar ;
      evidence.push({ type: "Global object", detail: `window.${raw.matchedGlobals[0]} is defined on the page`, strength: "strong" });
    }
  }
  if(raw.matchedUrls.length){
    score += weights.scriptPattern ;
    evidence.push({ type: "Script/resource URL", detail: raw.matchedUrls[0], strength: "strong" });
  }
  if(raw.matchedDom.length) {
    score += weights.domSelector;
    evidence.push({ type: "DOM element", detail: `Matched selector: ${raw.matchedDom[0]}`, strength: "medium" });
  }
  if (raw.platformHostMatch){
    score += weights.platformHost;
    evidence.push({ type: "Platform CDN", detail: "A generic FlexyPe platform host was found in loaded resources", strength: "weak" });
  }
  if (raw.matchedKeywordsLive && !raw.matchedUrls.length && !raw.matchedDom.length) {
    score += weights.keywordHint;
    evidence.push({ type: "Inline script text", detail: "Product name mentioned in an active inline script", strength: "weak" });
  }

  var confidence = "Not Detected";
  if(score >= thresholds.detected) confidence = "Detected";
  else if (score >= thresholds.likely) confidence = "Likely";

  // Disabled/commented-out signal: only meaningful when it's NOT already
  // live — a product can't be simultaneously "active" and "disabled".
  const disabledEvidence = [];
  if (raw.anyGlobalExplicitlyInactive) {
    const g = raw.globalStates.find((s) => s.state.active === false);
    disabledEvidence.push({
      type: "Global object flag",
      detail: `window.${g.name} exists but reports active: false — installed, not currently running`
    });
  }
  if(confidence === "Not Detected") {
    if (raw.matchedKeywordsInComments.length){
      disabledEvidence.push({
        type: "HTML comment",
        detail: `A commented-out block mentions "${raw.matchedKeywordsInComments[0]}"`
      });
    }
    if (raw.hiddenNodesForProduct.length) {
      disabledEvidence.push({
        type: "Hidden container",
        detail: `Found a hidden element matching this product's markup: ${raw.hiddenNodesForProduct[0].snippet}`
      });
    }
  }

  return {
    product: productName,
    score,
    confidence: confidence,
    evidence,
    possiblyDisabled: disabledEvidence.length > 0,
    disabledEvidence
  };
}

function runDetection(collectorOutput) {
  const weights = window.SIGNAL_WEIGHTS ;
  const thresholds = window.CONFIDENCE_THRESHOLDS ;
  let results = {};
  
  Object.keys(collectorOutput.productResults).forEach(product => {
    results[product] = scoreProduct(product, collectorOutput.productResults[product], weights, thresholds);
  });
  return results;
}
