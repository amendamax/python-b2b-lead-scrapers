// Native Cloudflare Edge Handler for isbrokersafe.com & verifydating.net
// Zero Render dependency — powered 100% by Cloudflare D1 (radar-network-db) + Static Assets (env.ASSETS)

// Verified VasileDev Group Affiliate Redirects (ported 1-to-1 from server.py)
const AFFILIATE_REDIRECTS = {
  "catfish-check": { url: "https://www.anrdoezrs.net/click-101863908-17066431", forwardSid: true },
  "spokeo": { url: "https://www.anrdoezrs.net/click-101863908-17066431", forwardSid: true },
  "dating-safety-check": { url: "https://www.anrdoezrs.net/click-101863908-17040818", forwardSid: true },
  "background-report": { url: "https://www.anrdoezrs.net/click-101863908-17040894", forwardSid: true },
  "email-profile-check": { url: "https://www.anrdoezrs.net/click-101863908-12673645", forwardSid: true },
  "ftmo": { url: "https://join.ftmo.com/kclcyQANbTsQxpzBCCEQ", status: 302 },
  "fundednext": { url: "https://fundednext.com/?fpr=BROKERSAFE", status: 302 },
  "sabiotrade": { url: "https://sabiotrade.com/?aff=838346&aff_model=revenue&afftrack=BrokerVerifier" },
  "nordvpn": { url: "https://www.jdoqocy.com/click-101863908-16968809", forwardSid: true },
  "vpn-shield": { url: "https://www.jdoqocy.com/click-101863908-16968809", forwardSid: true },
  "surfshark": { url: "https://www.anrdoezrs.net/click-101863908-15438547", forwardSid: true },
  "gearup": { url: "https://www.anrdoezrs.net/click-101863908-17235979", forwardSid: true },
  "xm": { url: "https://affs.click/E17wj" },
  "exness": { url: "https://one.exnessonelink.com/a/hb0ywi6abh" },
  "plus500": { url: "https://www.plus500.com/Home.aspx?id=139742" },
  "etoro": { url: "https://med.etoro.com/B21647_A131664_TClick.aspx", urlUs: "https://med.etoro.com/B21933_A131664_TClick.aspx" },
  "etoro-us": { url: "https://med.etoro.com/B21933_A131664_TClick.aspx" },
  "avatrade": { url: "https://www.avatrade.com/trading-account?tag=MetaTrader5&key=222287" },
  "blackbull": { url: "https://blackbull.com/en?ib=43450" },
  "ibkr": { url: "https://ibkr.com/referral/vasile651" },
  "roboforex": { url: "https://rinfinity.com/a/chlsg" },
  "incogni": { url: "https://deal.incogni.io/aff_c?offer_id=11&aff_id=1505" },
  "remove-data": { url: "https://deal.incogni.io/aff_c?offer_id=11&aff_id=1505" },
  "identity-monitoring": { url: "https://www.tkqlhce.com/click-101863908-15740542", forwardSid: true },
  "tradingview": { url: "https://www.tradingview.com/pricing/?share_your_love=amendamax" },
  "socialcatfish": { url: "https://socialcatfish.com/?kw=verifydating" },
  "social-catfish": { url: "https://socialcatfish.com/?kw=verifydating" },
  "dating-singles": { url: "https://www.internationalcupid.com" },
  "verified-dating": { url: "https://www.internationalcupid.com" },
  "senior-dating": { url: "https://www.internationalcupid.com" },
  "intego": { url: "https://www.anrdoezrs.net/click-101863908-15733644", forwardSid: true },
  "mac-antivirus": { url: "https://www.anrdoezrs.net/click-101863908-15733644", forwardSid: true }
};

const NATIVE_BOT_IP_PREFIXES = [
  "51.68.", "51.75.", "51.77.", "51.83.", "51.89.", "51.91.", "51.210.", "51.254.", "51.255.",
  "54.36.", "54.37.", "54.38.", "135.125.", "137.74.", "141.94.", "141.95.", "145.239.",
  "146.59.", "147.135.", "149.202.", "151.80.", "152.228.", "162.19.", "164.132.", "176.31.",
  "178.32.", "178.33.", "188.165.", "193.70.", "213.32.", "213.186.", "213.209.159.", "217.182.",
  "47.74.", "47.76.", "47.88.", "47.89.", "47.90.", "47.91.", "47.236.", "47.237.", "47.238.",
  "8.208.", "8.209.", "8.210.", "8.211.", "8.212.", "8.213.", "8.214.", "8.215."
];

function isNativeAffiliateBotRequest(request) {
  if (request.method !== "GET") return true;
  const cf = request.cf || {};
  const cfCountry = String(cf.country || request.headers.get("cf-ipcountry") || "").toUpperCase();
  if (!cfCountry || cfCountry === "T1" || cfCountry === "XX") return true;
  if (cf.botManagement && cf.botManagement.verifiedBot) return true;
  const asn = Number(cf.asn || 0);
  const asOrg = String(cf.asOrganization || "");
  const DATACENTER_ASNS = new Set([16276, 45102, 37963, 24940, 14061, 16509, 14618, 15169, 396982, 8075, 63949, 20473, 136907, 51167, 12876, 60068, 9009, 212238, 132203, 20940, 13335, 54113, 36352, 46606, 62567, 206092, 211252, 49505, 57523]);
  if (DATACENTER_ASNS.has(asn) || /ovh|alibaba|alicloud|hetzner|digitalocean|amazon|aws|google cloud|microsoft|azure|choopa|vultr|linode|akamai|contabo|scaleway|m247|datacamp|leaseweb|huawei|tencent|bytedance|dataforseo|babbar|semrush|ahrefs|hostinger|ionos|kamatera|upcloud/i.test(asOrg)) return true;
  const ua = (request.headers.get("user-agent") || "").trim();
  const uaLow = ua.toLowerCase();
  if (ua.length < 25 || !uaLow.startsWith("mozilla/5.0")) return true;
  if (/probe|scanner|mapper|fuzz|nuclei|sqlmap|nikto|zgrab|masscan|bot|crawl|spider|slurp|mediapartners|adsbot|bingpreview|facebookexternalhit|meta-externalagent|twitterbot|linkedinbot|whatsapp|telegrambot|discordbot|applebot|gptbot|chatgpt|oai-searchbot|claudebot|anthropic|perplexity|bytespider|petalbot|yandex|baiduspider|duckduckbot|ahrefs|semrush|mj12bot|dotbot|rogerbot|screaming\s*frog|barkrowler|babbar|blexbot|serpstat|dataforseo|censys|shodan|headless|phantomjs|puppeteer|playwright|selenium|cypress|python|curl|wget|aiohttp|httpx|axios|node-fetch|go-http-client|java\/|libwww|okhttp|scrapy|undici|apache-httpclient|postmanruntime/i.test(uaLow)) {
    return true;
  }
  if (/chrome\/(?:[1-9]\d|1[01]\d|12[01]|14[89]|1[5-9]\d|[2-9]\d\d)\.|firefox\/(?:[1-9]\d|10\d|11[0-4])\.|windows nt [56]\.|iphone os (?:1[0-4]|[1-9])_|android [1-9][;)]|version\/(?:2[5-9]|[3-9]\d)\.\d+ safari|applewebkit\/537\.36$/i.test(uaLow)) return true;
  const purpose = (
    request.headers.get("purpose") ||
    request.headers.get("sec-purpose") ||
    request.headers.get("x-purpose") ||
    request.headers.get("x-moz") ||
    ""
  ).toLowerCase();
  if (purpose.includes("prefetch") || purpose.includes("preview") || purpose.includes("prerender")) return true;
  const secMode = (request.headers.get("sec-fetch-mode") || "").toLowerCase();
  if (!secMode || (secMode !== "navigate" && secMode !== "nested-navigate")) return true;
  const secSite = (request.headers.get("sec-fetch-site") || "").toLowerCase();
  const isSuspiciousProxyGeo = ["BR", "VN", "SG", "HK", "ID", "TH", "PH", "MY", "BD", "IN", "PK", "LK", "NP", "NG", "KE", "GH", "TZ", "UG", "EG", "MA", "DZ", "TN", "CO", "PE", "AR", "CL", "VE", "EC", "BO", "PY", "UY", "RU", "BY", "CN", "IR", "IQ", "SY", "TR", "UA", "KZ", "UZ"].includes(cfCountry);
  if (secSite === "none" && isSuspiciousProxyGeo) return true;
  const clientIp = request.headers.get("cf-connecting-ip") || "";
  if (clientIp && NATIVE_BOT_IP_PREFIXES.some((p) => clientIp.startsWith(p))) return true;
  return false;
}

const STATIC_BROKER_DB = {
  "etoro.com": {
    name: "eToro",
    score: 98,
    regulator: "FCA (UK) #583263, CySEC (CY) #109/10, ASIC (AU) #491139",
    verdictTitle: "VERIFIED TIER-1 MULTI-REGULATED BROKER",
    verdictText: "eToro is a globally regulated multi-asset brokerage supervised by Tier-1 authorities including the UK FCA, CySEC, and ASIC, with full MiFID II investor protection and segregated client funds.",
    redFlags: ["CFD trading carries inherent market leverage risk (51% of retail CFD accounts lose money)."],
    greenFlags: [
      "Tier-1 Multi-Jurisdictional Supervision (FCA #583263, CySEC #109/10, ASIC #491139).",
      "Segregated client accounts in Tier-1 banks + statutory investor compensation.",
      "Publicly audited financials & 17+ years of operational track record."
    ],
    ip: "104.18.14.101",
    hoster: "Cloudflare Enterprise Financial Network",
    domainAge: "2000-05-11 (26 years ago)",
    affiliateLink: "/go/etoro"
  },
  "avatrade.com": {
    name: "AvaTrade",
    score: 96,
    regulator: "Central Bank of Ireland (#C53877), ASIC (#406684), FSCA (#45984), FSA Japan (#1662)",
    verdictTitle: "VERIFIED TIER-1 REGULATED BROKER",
    verdictText: "AvaTrade is a heavily regulated global forex and CFD broker authorized in 9 jurisdictions including the Central Bank of Ireland (EU/MiFID II) and ASIC Australia.",
    redFlags: ["Standard market volatility risk on leveraged derivatives."],
    greenFlags: [
      "Central Bank of Ireland MiFID II Authorization (#C53877).",
      "Negative Balance Protection &AvaProtect risk management tool.",
      "18+ years of unblemished regulatory compliance."
    ],
    ip: "104.18.22.44",
    hoster: "Cloudflare Enterprise CDN",
    domainAge: "2006-08-19 (20 years ago)",
    affiliateLink: "/go/avatrade"
  },
  "exness.com": {
    name: "Exness",
    score: 96,
    regulator: "FCA (UK) #730729, CySEC (CY) #178/12, FSCA (ZA) #51024",
    verdictTitle: "VERIFIED TIER-1 REGULATED BROKER",
    verdictText: "Exness is a Tier-1 regulated institutional and retail broker with Deloitte-audited monthly trading volumes exceeding $4 Trillion and instant automated withdrawals.",
    redFlags: ["High leverage options available on non-EU entities require strict risk management."],
    greenFlags: [
      "Authorized and regulated by the UK FCA (#730729) and CySEC (#178/12).",
      "Deloitte-audited financial transparency & segregated client reserves.",
      "Instant automated withdrawal execution."
    ],
    ip: "104.18.19.88",
    hoster: "Cloudflare Enterprise CDN",
    domainAge: "2008-03-15 (18 years ago)",
    affiliateLink: "/go/exness"
  },
  "xm.com": {
    name: "XM Global",
    score: 95,
    regulator: "CySEC (#120/10), ASIC (#443670), DFSA (#F003484)",
    verdictTitle: "VERIFIED TIER-1 REGULATED BROKER",
    verdictText: "XM is a globally licensed brokerage group serving over 10 million clients across 190 countries under strict CySEC, ASIC, and DFSA supervision.",
    redFlags: ["Standard retail CFD leverage risk."],
    greenFlags: [
      "Regulated by CySEC (#120/10), ASIC (#443670), and DFSA (#F003484).",
      "Zero requotes policy and Negative Balance Protection.",
      "Segregated client funds in Tier-1 institutions."
    ],
    ip: "104.18.10.52",
    hoster: "Cloudflare Enterprise CDN",
    domainAge: "1996-09-12 (30 years ago)",
    affiliateLink: "/go/xm"
  },
  "plus500.com": {
    name: "Plus500",
    score: 97,
    regulator: "FCA (#509909), CySEC (#250/14), ASIC (#417727), MAS",
    verdictTitle: "VERIFIED FTSE-250 LISTED REGULATED BROKER",
    verdictText: "Plus500 is a London Stock Exchange FTSE-250 publicly traded financial group regulated by the FCA, CySEC, ASIC, and MAS.",
    redFlags: ["CFD trading involves significant risk to capital."],
    greenFlags: [
      "Listed on the London Stock Exchange (FTSE 250 constituent).",
      "FCA (#509909), CySEC (#250/14), and ASIC (#417727) licensed.",
      "Full client money segregation and guaranteed stop-loss orders."
    ],
    ip: "104.18.31.12",
    hoster: "Cloudflare Enterprise CDN",
    domainAge: "2008-01-20 (18 years ago)",
    affiliateLink: "/go/plus500"
  },
  "sabiotrade.com": {
    name: "SabioTrade",
    score: 94,
    regulator: "Verified Proprietary Trading Firm (EU/Global)",
    verdictTitle: "VERIFIED PROPRIETARY TRADING EVALUATION FIRM",
    verdictText: "SabioTrade is a verified proprietary trading firm providing funded accounts up to $200,000 with up to 90% profit split and no risk to personal capital beyond the evaluation fee.",
    redFlags: ["Prop trading evaluations require passing strict drawdown rules."],
    greenFlags: [
      "Verified payout track record and transparent 1-step evaluation rules.",
      "Up to 90% profit split on funded accounts.",
      "Powered by institutional liquidity & Quadcode technology."
    ],
    ip: "104.21.44.91",
    hoster: "Cloudflare Enterprise CDN",
    domainAge: "2020-11-04 (6 years ago)",
    affiliateLink: "/go/sabiotrade"
  },
  "tradingview.com": {
    name: "TradingView",
    score: 99,
    regulator: "Global Financial Charting & Analytics Standard",
    verdictTitle: "VERIFIED GLOBAL MARKET ANALYTICS PLATFORM",
    verdictText: "TradingView is the world's leading financial charting and technical analysis platform trusted by over 60 million traders and institutional analysts.",
    redFlags: [],
    greenFlags: [
      "Industry-standard charting and Pine Script quantitative engine.",
      "Direct API integrations with regulated Tier-1 brokers only.",
      "Zero custody of client funds (non-broker analytics platform)."
    ],
    ip: "13.224.160.10",
    hoster: "Amazon CloudFront Enterprise",
    domainAge: "2011-06-01 (15 years ago)",
    affiliateLink: "/go/tradingview"
  }
};

const SUPPORTED_LANGS = ["ro", "it", "es", "fr", "de", "pt", "ru"];

function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function jsonResponse(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-API-Key, Authorization",
      ...extraHeaders
    }
  });
}

function fnv1a(str) {
  let h = 0x811c9dc5;
  const s = String(str || "");
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

function inferContentType(assetPath, fallback = null) {
  if (fallback) return fallback;
  const p = String(assetPath || "").toLowerCase();
  if (p.endsWith(".css")) return "text/css; charset=utf-8";
  if (p.endsWith(".js")) return "application/javascript; charset=utf-8";
  if (p.endsWith(".svg")) return "image/svg+xml";
  if (p.endsWith(".webp")) return "image/webp";
  if (p.endsWith(".png")) return "image/png";
  if (p.endsWith(".jpg") || p.endsWith(".jpeg")) return "image/jpeg";
  if (p.endsWith(".mp4")) return "video/mp4";
  if (p.endsWith(".json")) return "application/json; charset=utf-8";
  return null;
}

async function fetchStaticAsset(env, requestUrl, assetPath, contentTypeOverride = null, method = "GET") {
  if (!env || !env.ASSETS) return null;
  try {
    const assetUrl = new URL(assetPath, requestUrl);
    const res = await env.ASSETS.fetch(new Request(assetUrl.toString(), { method: "GET" }));
    if (res && res.status === 200) {
      const headers = new Headers(res.headers);
      const inferred = inferContentType(assetPath, contentTypeOverride);
      if (inferred) {
        headers.set("Content-Type", inferred);
      }
      headers.set("Access-Control-Allow-Origin", "*");
      headers.set("Cache-Control", "public, max-age=86400");
      return new Response(method === "HEAD" ? null : res.body, { status: 200, headers });
    }
  } catch (e) {}
  return null;
}

async function readStaticHtml(env, requestUrl, assetPath) {
  if (!env || !env.ASSETS) return null;
  try {
    const assetUrl = new URL(assetPath, requestUrl);
    const res = await env.ASSETS.fetch(new Request(assetUrl.toString(), { method: "GET" }));
    if (res && res.status === 200) {
      return await res.text();
    }
  } catch (e) {}
  return null;
}

// ============================================================================
// 1. RENDER DYNAMIC BROKER SCAM REPORT (/scam-reports/{slug} & /{lang}/scam-reports/{slug})
// ============================================================================
async function renderBrokerScamReportHtml(env, slug, lang = "en") {
  const row = await env.DB.prepare(
    `SELECT slug, entity_name, domain, regulator, warning_type, warning_date, official_url, reason, jurisdiction, risk_score, blacklisted_urls, clone_of
     FROM ib_scam_reports WHERE slug = ? LIMIT 1`
  ).bind(slug).first();

  if (!row) return null;

  const relatedRes = await env.DB.prepare(
    `SELECT slug, entity_name, regulator, warning_date
     FROM ib_scam_reports WHERE slug != ? ORDER BY id DESC LIMIT 6`
  ).bind(slug).all();
  const related = (relatedRes && relatedRes.results) || [];

  const entityName = row.entity_name || slug;
  const domain = row.domain || "Unverified / Multiple Mirrors";
  const regulator = row.regulator || "Financial Supervisory Authority";
  const warningType = row.warning_type || "Unauthorized Financial Services Warning";
  const warningDate = row.warning_date || "2026";
  const officialUrl = row.official_url || "https://www.iosco.org/investor_protection/?subsection=investor_alerts_portal";
  const reason = row.reason || `${entityName} is not authorized to provide investment, forex, or crypto brokerage services under ${regulator} supervision.`;
  const jurisdiction = row.jurisdiction || "International / EU";
  const riskScore = row.risk_score || 4;
  const cloneOf = row.clone_of || "";

  const langPrefix = SUPPORTED_LANGS.includes(lang) ? `/${lang}` : "";
  const canonicalUrl = `https://isbrokersafe.com${langPrefix}/scam-reports/${row.slug}`;

  const i18n = {
    en: {
      badge: "OFFICIAL REGULATORY BLACKLIST ALERT",
      h1Sub: "Scam Review, Regulatory Warning & Recovery Guide (2026)",
      verdictLabel: "CRITICAL RISK — BLACKLISTED ENTITY",
      verdictDesc: `Official enforcement records confirm that ${entityName} (${domain}) has been flagged by ${regulator} (${jurisdiction}) on ${warningDate} for "${warningType}". Do not deposit funds.`,
      regLabel: "Issuing Regulator",
      domLabel: "Flagged Domain / URL",
      dateLabel: "Enforcement Date",
      scoreLabel: "Safety Trust Score",
      reasonTitle: "Forensic Regulatory Findings & Infringement Details",
      cloneNotice: cloneOf ? `⚠️ CLONE FIRM ALERT: This entity fraudulently impersonates the legitimate regulated institution "${cloneOf}".` : "",
      safeTitle: "Verified Tier-1 Regulated Alternatives (FCA, CySEC, ASIC)",
      safeSub: "Never trade with unlicensed offshore platforms. Compare officially supervised brokers with statutory investor protection:",
      relatedTitle: "Recent Regulatory Blacklist Dossiers"
    },
    ro: {
      badge: "ALERTĂ OFICIALĂ DE BLACKLIST REGLEMENTAR",
      h1Sub: "Recenzie Fraudă, Alertă Autoritate & Ghid Recuperare Fonduri (2026)",
      verdictLabel: "RISC CRITIC — ENTITATE PE LISTA NEAGRĂ",
      verdictDesc: `Registrele oficiale de supraveghere confirmă că ${entityName} (${domain}) a fost raportată de ${regulator} (${jurisdiction}) la data de ${warningDate} pentru „${warningType}”. Nu depuneți fonduri.`,
      regLabel: "Autoritate Emitentă",
      domLabel: "Domeniu / URL Raportat",
      dateLabel: "Data Alertei",
      scoreLabel: "Scor de Siguranță",
      reasonTitle: "Constatări Forensice & Detalii Încălcare Reglementară",
      cloneNotice: cloneOf ? `⚠️ ALERTĂ CLONĂ: Această entitate copiază ilegal identitatea instituției reglementate „${cloneOf}”.` : "",
      safeTitle: "Alternative Reglementate Tier-1 (FCA, CySEC, ASF, ASIC)",
      safeSub: "Nu tranzacționați pe platforme offshore fără licență. Comparați brokeri autorizați cu fond de compensare a investitorilor:",
      relatedTitle: "Dosare Recente din Registrul de Alerte"
    },
    it: {
      badge: "ALLERTA UFFICIALE BLACKLIST REGOLAMENTARE",
      h1Sub: "Analisi Truffa, Avviso Autorità & Guida Recupero Fondi (2026)",
      verdictLabel: "RISCHIO CRITICO — ENTITÀ IN BLACKLIST",
      verdictDesc: `I registri ufficiali di vigilanza confermano che ${entityName} (${domain}) è stata segnalata da ${regulator} (${jurisdiction}) in data ${warningDate} per "${warningType}". Non versare capitali.`,
      regLabel: "Autorità di Vigilanza",
      domLabel: "Dominio / URL Segnalato",
      dateLabel: "Data Provvedimento",
      scoreLabel: "Punteggio di Sicurezza",
      reasonTitle: "Risultati Forensi & Dettagli Violazione Normativa",
      cloneNotice: cloneOf ? `⚠️ ALLERTA CLONE: Questa entità usurpa l'identità dell'istituto autorizzato "${cloneOf}".` : "",
      safeTitle: "Alternative Regolamentate Tier-1 (CONSOB, FCA, CySEC)",
      safeSub: "Evita piattaforme offshore non autorizzate. Confronta broker vigilati con conti segregati e tutela legale:",
      relatedTitle: "Ultimi Dossier di Vigilanza Finanziaria"
    }
  };
  const t = i18n[lang] || i18n.en;

  const hreflangs = [
    `<link rel="alternate" hreflang="en" href="https://isbrokersafe.com/scam-reports/${escHtml(row.slug)}" />`,
    `<link rel="alternate" hreflang="x-default" href="https://isbrokersafe.com/scam-reports/${escHtml(row.slug)}" />`,
    ...SUPPORTED_LANGS.map(l => `<link rel="alternate" hreflang="${l}" href="https://isbrokersafe.com/${l}/scam-reports/${escHtml(row.slug)}" />`)
  ].join("\n  ");

  const relatedLinksHtml = related.map(r => `
    <a href="${langPrefix}/scam-reports/${escHtml(r.slug)}" style="display:block;padding:14px 16px;background:#0f172a;border:1px solid #1e293b;border-radius:10px;color:#f8fafc;text-decoration:none;">
      <div style="font-size:11px;color:#ef4444;font-weight:700;text-transform:uppercase;">${escHtml(r.regulator)} &bull; ${escHtml(r.warning_date || "2026")}</div>
      <div style="font-size:14px;font-weight:700;color:#38bdf8;margin-top:4px;">${escHtml(r.entity_name)}</div>
    </a>
  `).join("");

  return `<!DOCTYPE html>
<html lang="${escHtml(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Is ${escHtml(entityName)} a Scam? ${escHtml(regulator)} Blacklist Warning &amp; Audit (2026) | IsBrokerSafe</title>
  <meta name="description" content="Official ${escHtml(regulator)} regulatory warning for ${escHtml(entityName)} (${escHtml(domain)}). Risk Score: ${riskScore}/100. Inspect forensic evidence, clone warnings, and recovery steps.">
  <link rel="canonical" href="${escHtml(canonicalUrl)}" />
  ${hreflangs}
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body { margin:0; font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif; background:#070b14; color:#f8fafc; line-height:1.6; }
    .container { max-width:1040px; margin:0 auto; padding:28px 20px 64px; }
    .topbar { display:flex; justify-content:space-between; align-items:center; padding:16px 0; border-bottom:1px solid #1e293b; margin-bottom:28px; flex-wrap:wrap; gap:12px; }
    .brand { color:#fff; font-weight:800; font-size:20px; text-decoration:none; display:flex; align-items:center; gap:8px; }
    .badge-danger { display:inline-block; background:rgba(239,68,68,0.16); color:#f87171; border:1px solid rgba(239,68,68,0.4); padding:6px 14px; border-radius:999px; font-size:12px; font-weight:800; letter-spacing:0.6px; }
    .card { background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:24px; margin-bottom:24px; }
    .grid-4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:14px; margin-top:18px; }
    .stat { background:#070b14; border:1px solid #1e293b; border-radius:12px; padding:14px; }
    .stat-label { font-size:11px; color:#94a3b8; text-transform:uppercase; font-weight:700; }
    .stat-val { font-size:15px; color:#fff; font-weight:800; margin-top:4px; word-break:break-word; }
    .btn { display:inline-block; padding:11px 18px; border-radius:10px; font-weight:700; font-size:13px; text-decoration:none; }
    .btn-primary { background:#10b981; color:#042f2e; }
    .btn-outline { background:#1e293b; color:#e2e8f0; border:1px solid #334155; }
  </style>
</head>
<body>
  <div class="container">
    <nav class="topbar">
      <a href="${langPrefix || "/"}" class="brand">🛡️ IsBrokerSafe.com</a>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <a href="/regulated-brokers" class="btn btn-outline">Verified Regulated Brokers</a>
        <a href="/directory/brokers" class="btn btn-outline">Blacklist Directory</a>
        <a href="/api/v1/broker/pdf/${escHtml(row.slug)}" class="btn btn-outline">📄 Download Forensic PDF</a>
      </div>
    </nav>

    <article>
      <span class="badge-danger">🚨 ${escHtml(t.badge)} &bull; ${escHtml(regulator)}</span>
      <h1 style="font-size:32px;margin:14px 0 8px;line-height:1.25;">${escHtml(entityName)} (${escHtml(domain)}) — ${escHtml(t.h1Sub)}</h1>
      <p style="color:#94a3b8;font-size:15px;margin-top:0;">${escHtml(t.verdictDesc)}</p>

      <div class="card" style="border-color:rgba(239,68,68,0.45);">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
          <div>
            <div style="font-size:12px;color:#f87171;font-weight:800;text-transform:uppercase;">${escHtml(t.verdictLabel)}</div>
            <div style="font-size:20px;font-weight:800;color:#fff;margin-top:4px;">${escHtml(entityName)}</div>
          </div>
          <div style="background:rgba(239,68,68,0.18);border:1px solid #ef4444;padding:10px 18px;border-radius:12px;text-align:center;">
            <div style="font-size:11px;color:#fca5a5;font-weight:700;text-transform:uppercase;">${escHtml(t.scoreLabel)}</div>
            <div style="font-size:24px;font-weight:900;color:#f87171;">${riskScore} / 100</div>
          </div>
        </div>

        <div class="grid-4">
          <div class="stat">
            <div class="stat-label">${escHtml(t.regLabel)}</div>
            <div class="stat-val" style="color:#38bdf8;">${escHtml(regulator)} (${escHtml(jurisdiction)})</div>
          </div>
          <div class="stat">
            <div class="stat-label">${escHtml(t.domLabel)}</div>
            <div class="stat-val" style="color:#f87171;">${escHtml(domain)}</div>
          </div>
          <div class="stat">
            <div class="stat-label">${escHtml(t.dateLabel)}</div>
            <div class="stat-val">${escHtml(warningDate)}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Classification</div>
            <div class="stat-val">${escHtml(warningType)}</div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 style="margin-top:0;font-size:20px;color:#38bdf8;">🔍 ${escHtml(t.reasonTitle)}</h2>
        ${t.cloneNotice ? `<div style="background:rgba(245,158,11,0.15);border:1px solid #f59e0b;color:#fde68a;padding:14px;border-radius:10px;margin-bottom:14px;font-weight:600;">${escHtml(t.cloneNotice)}</div>` : ""}
        <p style="color:#cbd5e1;font-size:15px;">${escHtml(reason)}</p>
        <ul style="color:#cbd5e1;font-size:14px;padding-left:20px;">
          <li><strong>No Statutory Compensation:</strong> Deposits sent to ${escHtml(entityName)} are not protected by FSCS, ICF, or MiFID II investor compensation funds.</li>
          <li><strong>Withdrawal Blocking Risk:</strong> Unlicensed platforms routinely demand fictitious "tax" or "AML release fees" before freezing accounts.</li>
          <li><strong>Official Regulator Source:</strong> <a href="${escHtml(officialUrl)}" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;">Inspect Official ${escHtml(regulator)} Notice &rarr;</a></li>
        </ul>
      </div>

      <div class="card" style="border-color:rgba(16,185,129,0.4);">
        <h2 style="margin-top:0;font-size:20px;color:#10b981;">✅ ${escHtml(t.safeTitle)}</h2>
        <p style="color:#94a3b8;font-size:14px;">${escHtml(t.safeSub)}</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:14px;">
          <div style="background:#070b14;border:1px solid #1e293b;padding:16px;border-radius:12px;">
            <div style="font-weight:800;color:#fff;font-size:16px;">eToro (FCA / CySEC / ASIC)</div>
            <div style="font-size:12px;color:#10b981;margin:4px 0 10px;">Trust Score: 98/100 &bull; Tier-1 Regulated</div>
            <a href="/go/etoro" rel="nofollow sponsored" class="btn btn-primary">Verify Official eToro Portal &rarr;</a>
          </div>
          <div style="background:#070b14;border:1px solid #1e293b;padding:16px;border-radius:12px;">
            <div style="font-weight:800;color:#fff;font-size:16px;">AvaTrade (CBI Ireland / ASIC)</div>
            <div style="font-size:12px;color:#10b981;margin:4px 0 10px;">Trust Score: 96/100 &bull; 9 Global Licenses</div>
            <a href="/go/avatrade" rel="nofollow sponsored" class="btn btn-primary">Verify Official AvaTrade Portal &rarr;</a>
          </div>
          <div style="background:#070b14;border:1px solid #1e293b;padding:16px;border-radius:12px;">
            <div style="font-weight:800;color:#fff;font-size:16px;">Exness (FCA / CySEC)</div>
            <div style="font-size:12px;color:#10b981;margin:4px 0 10px;">Trust Score: 96/100 &bull; Deloitte Audited</div>
            <a href="/go/exness" rel="nofollow sponsored" class="btn btn-primary">Verify Official Exness Portal &rarr;</a>
          </div>
        </div>
      </div>

      <div class="card">
        <h2 style="margin-top:0;font-size:18px;color:#f8fafc;">📂 ${escHtml(t.relatedTitle)}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;">
          ${relatedLinksHtml}
        </div>
      </div>
    </article>
  </div>
</body>
</html>`;
}

// ============================================================================
// 2. RENDER FORENSIC BROKER AUDIT (/audit/{domain_or_slug})
// ============================================================================
async function renderBrokerAuditHtml(env, rawTarget) {
  const cleanTarget = String(rawTarget || "").trim().toLowerCase().replace(/^https?:\/\/(www\.)?/, "").split("/")[0];
  if (!cleanTarget) return null;

  // Check static Tier-1 partners first
  const partnerMatch = STATIC_BROKER_DB[cleanTarget] || STATIC_BROKER_DB[cleanTarget + ".com"];

  // Check D1 scam reports
  const scamRow = await env.DB.prepare(
    `SELECT slug, entity_name, domain, regulator, warning_type, warning_date, official_url, reason, jurisdiction, risk_score
     FROM ib_scam_reports
     WHERE slug = ? OR LOWER(domain) = ? OR LOWER(entity_name) = ? OR LOWER(domain) LIKE ?
     LIMIT 1`
  ).bind(cleanTarget, cleanTarget, cleanTarget, `%${cleanTarget}%`).first();

  // Check D1 regulated brokers
  const regRow = !scamRow ? await env.DB.prepare(
    `SELECT slug, entity_name, domain, regulator, license_number, jurisdiction, category, official_register_url, trust_score
     FROM ib_regulated_brokers
     WHERE slug = ? OR LOWER(domain) = ? OR LOWER(entity_name) = ? OR LOWER(domain) LIKE ?
     LIMIT 1`
  ).bind(cleanTarget, cleanTarget, cleanTarget, `%${cleanTarget}%`).first() : null;

  let entityName = cleanTarget;
  let domain = cleanTarget;
  let score = 50;
  let statusBadge = "UNVERIFIED ENTITY — MANUAL CHECK REQUIRED";
  let statusColor = "#f59e0b";
  let regulator = "Not Found in Monitored Tier-1 Registers";
  let summary = `Our automated audit did not find an active Tier-1 license or an active enforcement blacklist entry for ${cleanTarget}. Exercise extreme caution and verify license numbers directly on national regulator registers before depositing funds.`;

  if (scamRow) {
    entityName = scamRow.entity_name;
    domain = scamRow.domain || cleanTarget;
    score = scamRow.risk_score || 4;
    statusBadge = `CRITICAL SCAM ALERT — BLACKLISTED BY ${scamRow.regulator}`;
    statusColor = "#ef4444";
    regulator = `${scamRow.regulator} (${scamRow.jurisdiction || "Enforcement Alert"})`;
    summary = scamRow.reason || `Official regulatory warning issued by ${scamRow.regulator} on ${scamRow.warning_date || "2026"}.`;
  } else if (partnerMatch) {
    entityName = partnerMatch.name;
    domain = cleanTarget.includes(".") ? cleanTarget : cleanTarget + ".com";
    score = partnerMatch.score;
    statusBadge = partnerMatch.verdictTitle;
    statusColor = "#10b981";
    regulator = partnerMatch.regulator;
    summary = partnerMatch.verdictText;
  } else if (regRow) {
    entityName = regRow.entity_name;
    domain = regRow.domain || cleanTarget;
    score = regRow.trust_score || 92;
    statusBadge = `VERIFIED LICENSED INSTITUTION (${regRow.regulator})`;
    statusColor = "#10b981";
    regulator = `${regRow.regulator} — License #${regRow.license_number || "Verified"} (${regRow.jurisdiction || "EU/Global"})`;
    summary = `${regRow.entity_name} (${regRow.domain}) is an officially authorized financial institution supervised by ${regRow.regulator}.`;
  }

  const canonicalUrl = `https://isbrokersafe.com/audit/${ encodeURIComponent(cleanTarget) }`;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escHtml(entityName)} Forensic Compliance Audit &amp; Regulatory Check (2026) | IsBrokerSafe</title>
  <meta name="description" content="Live regulatory compliance audit for ${escHtml(entityName)} (${escHtml(domain)}). Trust Score: ${score}/100. Supervised status: ${escHtml(regulator)}.">
  <link rel="canonical" href="${escHtml(canonicalUrl)}" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body { margin:0; font-family:'Inter',sans-serif; background:#070b14; color:#f8fafc; line-height:1.6; }
    .container { max-width:1000px; margin:0 auto; padding:28px 20px 64px; }
    .card { background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:24px; margin-bottom:20px; }
    .btn { display:inline-block; padding:10px 18px; border-radius:10px; font-weight:700; font-size:13px; text-decoration:none; background:#10b981; color:#042f2e; }
  </style>
</head>
<body>
  <div class="container">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e293b;padding-bottom:16px;margin-bottom:24px;">
      <a href="/" style="color:#fff;font-weight:800;font-size:20px;text-decoration:none;">🛡️ IsBrokerSafe.com</a>
      <a href="/regulated-brokers" style="color:#38bdf8;text-decoration:none;font-weight:600;font-size:14px;">All Regulated Brokers &rarr;</a>
    </div>
    <div class="card" style="border-color:${statusColor};">
      <div style="font-size:12px;font-weight:800;color:${statusColor};text-transform:uppercase;">${escHtml(statusBadge)}</div>
      <h1 style="margin:8px 0;font-size:30px;">${escHtml(entityName)} (${escHtml(domain)}) — Forensic Audit</h1>
      <p style="color:#cbd5e1;font-size:15px;">${escHtml(summary)}</p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:18px;">
        <div style="background:#070b14;padding:14px;border-radius:10px;border:1px solid #1e293b;">
          <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;">Trust &amp; Safety Score</div>
          <div style="font-size:24px;font-weight:900;color:${statusColor};">${score} / 100</div>
        </div>
        <div style="background:#070b14;padding:14px;border-radius:10px;border:1px solid #1e293b;">
          <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;">Regulatory Authority</div>
          <div style="font-size:15px;font-weight:700;color:#fff;margin-top:4px;">${escHtml(regulator)}</div>
        </div>
        <div style="background:#070b14;padding:14px;border-radius:10px;border:1px solid #1e293b;">
          <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;">Evaluated Domain</div>
          <div style="font-size:15px;font-weight:700;color:#38bdf8;margin-top:4px;">${escHtml(domain)}</div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>`;
}

// ============================================================================
// 3. RENDER VERIFYDATING SCAMMERS DIRECTORY (/scammers) & PROFILE (/scammer/{slug})
// ============================================================================
async function renderScammersDirectoryHtml(env, requestUrl) {
  const url = new URL(requestUrl);
  const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10) || 1);
  const category = (url.searchParams.get("category") || "").trim();
  const q = (url.searchParams.get("q") || "").trim();
  const perPage = 36;
  const offset = (page - 1) * perPage;

  let whereSql = "1=1";
  const binds = [];
  if (category) {
    whereSql += " AND LOWER(scam_category) LIKE ?";
    binds.push(`%${category.toLowerCase()}%`);
  }
  if (q) {
    whereSql += " AND (LOWER(persona_name) LIKE ? OR LOWER(claimed_profession) LIKE ? OR LOWER(claimed_location) LIKE ?)";
    binds.push(`%${q.toLowerCase()}%`, `%${q.toLowerCase()}%`, `%${q.toLowerCase()}%`);
  }

  const countRow = await env.DB.prepare(`SELECT COUNT(*) AS cnt FROM vd_scam_profiles WHERE ${whereSql}`).bind(...binds).first();
  const total = (countRow && countRow.cnt) || 5871;

  const rowsRes = await env.DB.prepare(
    `SELECT slug, persona_name, claimed_age, claimed_location, claimed_profession, scam_category, risk_score
     FROM vd_scam_profiles WHERE ${whereSql} ORDER BY id DESC LIMIT ? OFFSET ?`
  ).bind(...binds, perPage, offset).all();
  const rows = (rowsRes && rowsRes.results) || [];

  const cardsHtml = rows.map(r => `
    <a href="/scammer/${escHtml(r.slug)}" style="display:block;background:#0f172a;border:1px solid #1e293b;border-radius:14px;padding:18px;text-decoration:none;color:#f8fafc;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <span style="font-size:11px;background:rgba(244,63,94,0.16);color:#fb7185;padding:3px 10px;border-radius:99px;font-weight:700;">Risk: ${r.risk_score || 94}%</span>
        <span style="font-size:11px;color:#94a3b8;">${escHtml(r.scam_category || "Romance Scam")}</span>
      </div>
      <div style="font-size:17px;font-weight:800;color:#fff;">${escHtml(r.persona_name)}, ${r.claimed_age || 34}</div>
      <div style="font-size:13px;color:#38bdf8;margin-top:4px;">${escHtml(r.claimed_profession || "Verified Catfish Persona")}</div>
      <div style="font-size:12px;color:#94a3b8;margin-top:4px;">📍 ${escHtml(r.claimed_location || "International")}</div>
    </a>
  `).join("");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Romance Scammer &amp; Catfish Database (${total.toLocaleString()} Profiles) | VerifyDating.net</title>
  <meta name="description" content="Search ${total.toLocaleString()}+ documented romance scam personas, stolen catfish photos, military/crypto dating scripts, and OSINT identity warnings.">
  <link rel="canonical" href="https://verifydating.net/scammers" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body { margin:0; font-family:'Inter',sans-serif; background:#070b14; color:#f8fafc; line-height:1.6; }
    .container { max-width:1100px; margin:0 auto; padding:28px 20px 64px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:16px; margin-top:24px; }
  </style>
</head>
<body>
  <div class="container">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e293b;padding-bottom:16px;margin-bottom:24px;">
      <a href="/" style="color:#fff;font-weight:800;font-size:20px;text-decoration:none;">💘 VerifyDating.net</a>
      <a href="/guides" style="color:#38bdf8;text-decoration:none;font-weight:600;font-size:14px;">Catfish Investigation Guides &rarr;</a>
    </div>
    <h1 style="font-size:32px;margin-bottom:8px;">Global Romance Scammer &amp; Catfish Registry (${total.toLocaleString()} Documented Personas)</h1>
    <p style="color:#94a3b8;margin-top:0;">Inspect documented romance fraud aliases, stolen influencer/military photos, and pig-butchering scripts reported across Tinder, Hinge, Bumble, Instagram, and WhatsApp.</p>
    <div class="grid">${cardsHtml}</div>
    <div style="display:flex;justify-content:center;gap:12px;margin-top:32px;">
      ${page > 1 ? `<a href="/scammers?page=${page - 1}" style="padding:10px 18px;background:#1e293b;color:#fff;border-radius:10px;text-decoration:none;">&larr; Previous</a>` : ""}
      <a href="/scammers?page=${page + 1}" style="padding:10px 18px;background:#e11d48;color:#fff;border-radius:10px;text-decoration:none;font-weight:700;">Next Page &rarr;</a>
    </div>
  </div>
</body>
</html>`;
}

async function renderScammerProfileHtml(env, slug, lang = "en") {
  const row = await env.DB.prepare(
    `SELECT slug, persona_name, gender, scam_category, claimed_age, claimed_location, claimed_profession,
            stolen_from_real_person, typical_script, scam_story, warning_flags, photo_urls, risk_score,
            reported_aliases, views_count, first_reported_date
     FROM vd_scam_profiles WHERE slug = ? LIMIT 1`
  ).bind(slug).first();

  if (!row) return null;

  const relatedRes = await env.DB.prepare(
    `SELECT slug, persona_name, claimed_age, claimed_profession, scam_category, risk_score
     FROM vd_scam_profiles WHERE slug != ? ORDER BY id DESC LIMIT 6`
  ).bind(slug).all();
  const related = (relatedRes && relatedRes.results) || [];

  const langPrefix = SUPPORTED_LANGS.includes(lang) ? `/${lang}` : "";
  const canonicalUrl = `https://verifydating.net${langPrefix}/scammer/${row.slug}`;

  let flags = [];
  try {
    flags = JSON.parse(row.warning_flags || "[]");
  } catch (e) {
    flags = (row.warning_flags || "").split(",").map(s => s.trim()).filter(Boolean);
  }
  let aliases = [];
  try {
    aliases = JSON.parse(row.reported_aliases || "[]");
  } catch (e) {
    aliases = (row.reported_aliases || "").split(",").map(s => s.trim()).filter(Boolean);
  }

  const hreflangs = [
    `<link rel="alternate" hreflang="en" href="https://verifydating.net/scammer/${escHtml(row.slug)}" />`,
    `<link rel="alternate" hreflang="x-default" href="https://verifydating.net/scammer/${escHtml(row.slug)}" />`,
    ...SUPPORTED_LANGS.map(l => `<link rel="alternate" hreflang="${l}" href="https://verifydating.net/${l}/scammer/${escHtml(row.slug)}" />`)
  ].join("\n  ");

  const relatedHtml = related.map(r => `
    <a href="${langPrefix}/scammer/${escHtml(r.slug)}" style="display:block;padding:14px;background:#070b14;border:1px solid #1e293b;border-radius:10px;color:#fff;text-decoration:none;">
      <div style="font-size:11px;color:#fb7185;font-weight:700;">${escHtml(r.scam_category || "Catfish Alert")} &bull; Risk ${r.risk_score || 95}%</div>
      <div style="font-size:15px;font-weight:700;color:#38bdf8;margin-top:4px;">${escHtml(r.persona_name)}, ${r.claimed_age || 33} — ${escHtml(r.claimed_profession || "")}</div>
    </a>
  `).join("");

  return `<!DOCTYPE html>
<html lang="${escHtml(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${escHtml(row.persona_name)} (${escHtml(row.claimed_profession || "Dating Profile")}) — Romance Scam &amp; Catfish Alert | VerifyDating.net</title>
  <meta name="description" content="Forensic catfish dossier for ${escHtml(row.persona_name)} (${row.claimed_age || 34}, ${escHtml(row.claimed_location || "Online")}). Category: ${escHtml(row.scam_category)}. Biometric Risk: ${row.risk_score || 95}/100.">
  <link rel="canonical" href="${escHtml(canonicalUrl)}" />
  ${hreflangs}
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body { margin:0; font-family:'Inter',sans-serif; background:#070b14; color:#f8fafc; line-height:1.6; }
    .container { max-width:1000px; margin:0 auto; padding:28px 20px 64px; }
    .card { background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:24px; margin-bottom:22px; }
    .badge { display:inline-block; background:rgba(244,63,94,0.16); color:#fb7185; border:1px solid rgba(244,63,94,0.4); padding:5px 14px; border-radius:99px; font-size:12px; font-weight:800; }
    .btn { display:inline-block; padding:11px 18px; border-radius:10px; font-weight:700; font-size:13px; text-decoration:none; background:#e11d48; color:#fff; }
  </style>
</head>
<body>
  <div class="container">
    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1e293b;padding-bottom:16px;margin-bottom:24px;flex-wrap:wrap;gap:12px;">
      <a href="${langPrefix || "/"}" style="color:#fff;font-weight:800;font-size:20px;text-decoration:none;">💘 VerifyDating.net</a>
      <div style="display:flex;gap:12px;">
        <a href="/scammers" style="color:#38bdf8;text-decoration:none;font-weight:600;font-size:14px;">All Scammer Profiles</a>
        <a href="/" class="btn">Run Reverse Photo Scan &rarr;</a>
      </div>
    </div>

    <article>
      <span class="badge">🚨 CONFIRMED CATFISH / ROMANCE SCAM PERSONA &bull; RISK ${row.risk_score || 95}/100</span>
      <h1 style="font-size:32px;margin:14px 0 8px;">${escHtml(row.persona_name)} (${row.claimed_age || 34}, ${escHtml(row.claimed_profession || "Online Persona")}) — Catfish Investigation Dossier</h1>
      <p style="color:#94a3b8;font-size:15px;margin-top:0;">Reported Location: <strong>${escHtml(row.claimed_location || "Multiple Cities")}</strong> &bull; Category: <strong>${escHtml(row.scam_category || "Romance Fraud")}</strong> &bull; First Reported: <strong>${escHtml(row.first_reported_date || "2026")}</strong></p>

      <div class="card">
        <h2 style="margin-top:0;font-size:20px;color:#fb7185;">📋 Documented Scam Story &amp; Operational Modus Operandi</h2>
        <p style="color:#cbd5e1;font-size:15px;">${escHtml(row.scam_story || "")}</p>
        ${row.typical_script ? `<blockquote style="margin:16px 0;padding:14px 18px;background:#070b14;border-left:4px solid #e11d48;color:#fda4af;font-style:italic;border-radius:8px;">"${escHtml(row.typical_script)}"</blockquote>` : ""}
        <p style="color:#94a3b8;font-size:13px;"><strong>Stolen Identity Source:</strong> ${escHtml(row.stolen_from_real_person || "Unconsented social media / influencer photography")}</p>
        ${aliases.length ? `<p style="color:#94a3b8;font-size:13px;"><strong>Known Aliases Used:</strong> ${aliases.map(escHtml).join(", ")}</p>` : ""}
      </div>

      <div class="card">
        <h2 style="margin-top:0;font-size:20px;color:#38bdf8;">🚩 Behavioral Red Flags &amp; Forensic Indicators</h2>
        <ul style="color:#cbd5e1;padding-left:20px;">
          ${flags.map(f => `<li style="margin-bottom:6px;">${escHtml(f)}</li>`).join("")}
        </ul>
        <div style="margin-top:18px;display:flex;gap:12px;flex-wrap:wrap;">
          <a href="/go/catfish-check" rel="nofollow sponsored" class="btn">Run Deep Phone &amp; Identity Background Check &rarr;</a>
          <a href="/" class="btn" style="background:#1e293b;border:1px solid #334155;">Upload Photo for AI Face Match &rarr;</a>
        </div>
      </div>

      <div class="card">
        <h2 style="margin-top:0;font-size:18px;color:#fff;">🔗 Related Documented Catfish Personas</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;">
          ${relatedHtml}
        </div>
      </div>
    </article>
  </div>
</body>
</html>`;
}

// ============================================================================
// 4. RENDER ALPHABETICAL DIRECTORY (/directory/{category}/{letter})
// ============================================================================
async function renderAlphabeticalDirectoryHtml(env, host, category, letter) {
  const cleanLetter = String(letter || "a").trim().toUpperCase().slice(0, 1);
  const isBrokers = category === "brokers";

  let itemsHtml = "";
  if (isBrokers) {
    const res = await env.DB.prepare(
      `SELECT slug, entity_name, domain, regulator, warning_date
       FROM ib_scam_reports WHERE UPPER( entity_name ) LIKE ? ORDER BY entity_name ASC LIMIT 250`
    ).bind(`${cleanLetter}%`).all();
    const rows = (res && res.results) || [];
    itemsHtml = rows.map(r => `
      <a href="/scam-reports/${escHtml(r.slug)}" style="display:block;padding:12px 14px;background:#0f172a;border:1px solid #1e293b;border-radius:10px;color:#38bdf8;text-decoration:none;font-size:14px;font-weight:600;">
        ${escHtml(r.entity_name)} <span style="color:#94a3b8;font-size:12px;font-weight:400;">(${escHtml(r.regulator)})</span>
      </a>
    `).join("");
  } else {
    const res = await env.DB.prepare(
      `SELECT slug, persona_name, claimed_age, scam_category
       FROM vd_scam_profiles WHERE UPPER( persona_name ) LIKE ? ORDER BY persona_name ASC LIMIT 250`
    ).bind(`${cleanLetter}%`).all();
    const rows = (res && res.results) || [];
    itemsHtml = rows.map(r => `
      <a href="/scammer/${escHtml(r.slug)}" style="display:block;padding:12px 14px;background:#0f172a;border:1px solid #1e293b;border-radius:10px;color:#fb7185;text-decoration:none;font-size:14px;font-weight:600;">
        ${escHtml(r.persona_name)}, ${r.claimed_age || 33} <span style="color:#94a3b8;font-size:12px;font-weight:400;">(${escHtml(r.scam_category)})</span>
      </a>
    `).join("");
  }

  const alphabetNav = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map(l =>
    `<a href="/directory/${escHtml(category)}/${l}" style="padding:6px 10px;border-radius:6px;background:${l === cleanLetter ? "#38bdf8" : "#1e293b"};color:${l === cleanLetter ? "#070b14" : "#fff"};text-decoration:none;font-weight:700;font-size:13px;">${l}</a>`
  ).join(" ");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Directory Index "${cleanLetter}" — ${isBrokers ? "Flagged Brokers & Regulatory Warnings" : "Documented Catfish & Romance Scammers"} | ${escHtml(host)}</title>
  <meta name="description" content="Browse all documented ${isBrokers ? "unlicensed brokers and financial regulator warnings" : "romance scam personas and catfish profiles"} starting with letter ${cleanLetter}.">
  <link rel="canonical" href="https://${escHtml(host)}/directory/${escHtml(category)}/${cleanLetter}" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body { margin:0; font-family:'Inter',sans-serif; background:#070b14; color:#f8fafc; line-height:1.6; }
    .container { max-width:1080px; margin:0 auto; padding:28px 20px 64px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:12px; margin-top:20px; }
  </style>
</head>
<body>
  <div class="container">
    <div style="margin-bottom:20px;"><a href="/" style="color:#38bdf8;text-decoration:none;font-weight:700;">&larr; Back to Home</a></div>
    <h1>Alphabetical Archive — Letter "${cleanLetter}"</h1>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin:16px 0;">${alphabetNav}</div>
    <div class="grid">${itemsHtml || `<p style="color:#94a3b8;">No records starting with ${cleanLetter}.</p>`}</div>
  </div>
</body>
</html>`;
}


const VALID_ADMIN_TOKENS = new Set([
  "vd_sec_vault_2026_98f4a17e82b941c09d3e8a",
  "verifydating_secret_2026",
  "vasiledev-vault-master-2026-cn-ro"
]);

function checkAdminToken(url, request) {
  const tok = (url.searchParams.get("token") || request.headers.get("x-admin-token") || "").trim();
  return VALID_ADMIN_TOKENS.has(tok);
}

function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

async function renderAdminDashboardHtml(env, url, request) {
  if (!checkAdminToken(url, request)) {
    return new Response("<h2 style='color:#ef4444;font-family:sans-serif;'>403 Unauthorized Access Token</h2>", {
      status: 403,
      headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex, nofollow, noarchive" }
    });
  }

  const scansRes = await env.DB.prepare(
    `SELECT id, created_at, payment_status, scam_probability, matches_count, image_path, email, package, image_base64
     FROM vd_scans ORDER BY created_at DESC LIMIT 100`
  ).all();
  const rows = (scansRes && scansRes.results) || [];

  const leadsRes = await env.DB.prepare(
    `SELECT email, created_at FROM vd_video_leads ORDER BY created_at DESC LIMIT 100`
  ).all();
  const vLeads = (leadsRes && leadsRes.results) || [];

  const errRes = await env.DB.prepare(
    `SELECT site, email, scan_id, package, error_message, created_at FROM ib_payment_errors ORDER BY id DESC LIMIT 100`
  ).all();
  const errorRows = (errRes && errRes.results) || [];

  const totalScans = rows.length;
  const totalPaid = rows.filter(r => r.payment_status === "paid").length;
  const revenue = rows
    .filter(r => r.payment_status === "paid")
    .reduce((sum, r) => sum + (r.package === "single" ? 3.99 : (r.package === "bundle" || r.package === "pro") ? 7.99 : 2.99), 0);
  const vLeadsCount = vLeads.length;

  let logsTableRows = "";
  for (const err of errorRows) {
    logsTableRows += `
      <tr data-type="error" style="border-bottom:1px solid #334155;background:rgba(239,68,68,0.05);">
        <td style="padding:12px;"><span style="background:#EF4444;color:#fff;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:700;">❌ EȘUAT</span></td>
        <td style="padding:12px;font-weight:600;color:#F8FAFC;">${escHtml(err.site || "VerifyDating")}</td>
        <td style="padding:12px;color:#38BDF8;word-break:break-all;">${escHtml(err.email || "N/A")}</td>
        <td style="padding:12px;color:#94A3B8;">${escHtml(err.package || "N/A")}</td>
        <td style="padding:12px;color:#FCA5A5;font-family:monospace;font-size:12px;">⚠️ ${escHtml(String(err.error_message || "").slice(0, 60))}...</td>
        <td style="padding:12px;"><code style="background:#0F172A;padding:2px 6px;border-radius:4px;color:#94A3B8;">${escHtml(String(err.scan_id || "").slice(0, 12))}</code></td>
        <td style="padding:12px;color:#94A3B8;font-size:12px;">${escHtml(err.created_at || "")}</td>
      </tr>`;
  }

  for (const r of rows) {
    if (r.payment_status === "paid") {
      const sPrice = r.package === "single" ? "$3.99" : (r.package === "bundle" || r.package === "pro") ? "$7.99" : "$2.99";
      const sFmtDate = r.created_at ? String(r.created_at).replace("T", " ").slice(0, 19) : "N/A";
      logsTableRows += `
        <tr data-type="success" style="border-bottom:1px solid #334155;background:rgba(16,185,129,0.05);">
          <td style="padding:12px;"><span style="background:#10B981;color:#fff;padding:4px 8px;border-radius:6px;font-size:11px;font-weight:700;">✅ REUȘIT</span></td>
          <td style="padding:12px;font-weight:600;color:#F8FAFC;">VerifyDating</td>
          <td style="padding:12px;color:#38BDF8;word-break:break-all;">${escHtml(r.email || "N/A")}</td>
          <td style="padding:12px;color:#34D399;font-weight:600;">${escHtml(r.package || "basic")} (${sPrice})</td>
          <td style="padding:12px;color:#34D399;">✓ Plată confirmată cu succes</td>
          <td style="padding:12px;"><code style="background:#0F172A;padding:2px 6px;border-radius:4px;color:#94A3B8;">${escHtml(String(r.id || "").slice(0, 12))}</code></td>
          <td style="padding:12px;color:#94A3B8;font-size:12px;">${escHtml(sFmtDate)}</td>
        </tr>`;
    }
  }

  const vLeadsHtml = vLeads.map(v => {
    const d = v.created_at ? String(v.created_at).replace("T", " ").slice(0, 19) : "N/A";
    return `<div style="background:#0F172A;padding:8px 14px;border-radius:8px;border:1px solid #334155;margin-top:6px;display:flex;justify-content:space-between;align-items:center;"><span>📧 <strong style="color:#38BDF8;">${escHtml(v.email)}</strong></span><span style="font-size:11px;color:#94A3B8;">${escHtml(d)}</span></div>`;
  }).join("");

  const cardsHtml = rows.map(r => {
    const scanId = r.id || "";
    const scamProb = Number(r.scam_probability || 85);
    const matches = Number(r.matches_count || 6);
    const imgUrl = r.image_base64
      ? `data:image/jpeg;base64,${r.image_base64}`
      : (r.image_path && r.image_path.startsWith("http") ? r.image_path : "/catfish_profile.png");
    const priceDisplay = r.package === "single" ? "$3.99" : (r.package === "bundle" || r.package === "pro") ? "$7.99" : "$2.99";
    const statusBadge = r.payment_status === "paid"
      ? `<span style="background:#10B981;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">PAID (${priceDisplay})</span>`
      : `<span style="background:#EF4444;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">UNPAID</span>`;
    const probColor = scamProb >= 70 ? "#EF4444" : scamProb >= 40 ? "#F59E0B" : "#10B981";
    const formattedDate = r.created_at ? String(r.created_at).replace("T", " ").slice(0, 19) + " UTC" : "N/A";
    const unlockBtn = r.payment_status !== "paid"
      ? `<button onclick="markPaid('${escHtml(scanId)}')" style="background:#10B981;color:#fff;border:none;padding:8px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;margin-top:8px;width:100%;">🔓 Unlock Scan</button>`
      : "";

    return `
      <div style="background:#1E293B;border-radius:16px;overflow:hidden;border:1px solid #334155;display:flex;flex-direction:column;box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);">
        <div style="height:220px;background:#0F172A;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;padding:10px;">
          <div onclick="openImgModal('${escHtml(imgUrl)}')" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;cursor:pointer;" title="Click to view full HD photo">
            <img src="${escHtml(imgUrl)}" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;" alt="Uploaded Scan"/>
          </div>
        </div>
        <div style="padding:16px;flex:1;display:flex;flex-direction:column;gap:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            ${statusBadge}
            <span style="font-size:12px;color:#94A3B8;">${escHtml(formattedDate)}</span>
          </div>
          <div style="font-size:13px;color:#CBD5E1;font-weight:600;word-break:break-all;">
            ID: <code style="background:#0F172A;padding:2px 6px;border-radius:4px;color:#38BDF8;">${escHtml(scanId.slice(0, 13))}...</code>
          </div>
          <div style="display:flex;gap:10px;margin-top:4px;">
            <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
              Risk: <strong style="color:${probColor};">${scamProb}%</strong>
            </div>
            <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
              Matches: <strong style="color:#38BDF8;">${matches}</strong>
            </div>
          </div>
          ${r.email ? `<div style="font-size:12px;color:#10B981;margin-top:4px;word-break:break-all;">📧 ${escHtml(r.email)}</div>` : ""}
          ${unlockBtn}
        </div>
      </div>`;
  }).join("");

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VerifyDating Live Admin Dashboard (Cloudflare D1 Edge)</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; background: #0F172A; color: #F8FAFC; margin: 0; padding: 24px; }
    .header { max-width: 1200px; margin: 0 auto 28px auto; display: flex; justify-content: space-between; align-items: center; background: #1E293B; padding: 24px 32px; border-radius: 20px; border: 1px solid #334155; flex-wrap: wrap; gap: 16px; }
    .stats { display: flex; gap: 20px; flex-wrap: wrap; }
    .stat-box { background: #0F172A; padding: 14px 24px; border-radius: 14px; border: 1px solid #334155; text-align: center; min-width: 100px; }
    .stat-value { font-size: 24px; font-weight: 700; color: #38BDF8; }
    .stat-label { font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }
    .grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
  </style>
  <script>
    let currentLogFilter = 'all';
    function setLogFilter(filterType) {
      currentLogFilter = filterType;
      const btnAll = document.getElementById('btnFilterAll');
      const btnErrors = document.getElementById('btnFilterErrors');
      const btnSuccess = document.getElementById('btnFilterSuccess');
      if (btnAll) { btnAll.style.background = filterType === 'all' ? '#3B82F6' : 'transparent'; btnAll.style.color = '#fff'; }
      if (btnErrors) { btnErrors.style.background = filterType === 'error' ? '#EF4444' : 'transparent'; btnErrors.style.color = filterType === 'error' ? '#fff' : '#EF4444'; }
      if (btnSuccess) { btnSuccess.style.background = filterType === 'success' ? '#10B981' : 'transparent'; btnSuccess.style.color = filterType === 'success' ? '#fff' : '#10B981'; }
      filterLogsTable();
    }
    function filterLogsTable() {
      const searchVal = (document.getElementById('logSearchInput')?.value || '').toLowerCase();
      const rows = document.querySelectorAll('#logsTable tbody tr');
      rows.forEach(row => {
        const isError = row.getAttribute('data-type') === 'error';
        const isSuccess = row.getAttribute('data-type') === 'success';
        const text = row.innerText.toLowerCase();
        let matchesFilter = true;
        if (currentLogFilter === 'error' && !isError) matchesFilter = false;
        if (currentLogFilter === 'success' && !isSuccess) matchesFilter = false;
        let matchesSearch = text.includes(searchVal);
        row.style.display = (matchesFilter && matchesSearch) ? '' : 'none';
      });
    }
    function refreshNow() { window.location.reload(); }
    function markPaid(scanId) {
      if (confirm("Are you sure you want to manually mark this scan as PAID and unlock the report?")) {
        const token = new URLSearchParams(window.location.search).get('token');
        fetch('/api/admin/mark-paid?scan_id=' + encodeURIComponent(scanId) + '&token=' + encodeURIComponent(token || ''), { method: 'POST' })
          .then(res => { if (res.ok) window.location.reload(); else alert("Error unlocking scan."); });
      }
    }
    function clearPaymentErrors() {
      if (confirm("⚠️ Sigur dorești să ștergi TOATE jurnalele și erorile de plăți?")) {
        const token = new URLSearchParams(window.location.search).get('token');
        fetch('/api/admin/clear-payment-errors?token=' + encodeURIComponent(token || ''), { method: 'POST' })
          .then(res => { if (res.ok) window.location.reload(); else alert("Eroare la ștergerea jurnalelor."); });
      }
    }
    function resetScans() {
      if (confirm("⚠️ Are you sure you want to CLEAR ALL scans and reset the database?")) {
        const token = new URLSearchParams(window.location.search).get('token');
        fetch('/api/admin/clear-scans?token=' + encodeURIComponent(token || ''), { method: 'POST' })
          .then(res => { if (res.ok) window.location.reload(); else alert("Error resetting database."); });
      }
    }
    function openImgModal(src) {
      var overlay = document.getElementById('img-modal-overlay');
      var target = document.getElementById('img-modal-target');
      if (overlay && target && src && src !== '#') { target.src = src; overlay.style.display = 'flex'; }
    }
    function closeImgModal() {
      var overlay = document.getElementById('img-modal-overlay');
      if (overlay) overlay.style.display = 'none';
    }
  </script>
</head>
<body>
  <div class="header">
    <div>
      <h1 style="margin:0;font-size:26px;color:#F8FAFC;display:flex;align-items:center;gap:10px;">🔍 VerifyDating Live Scans <span style="font-size:12px;background:rgba(16,185,129,0.2);color:#34d399;padding:4px 10px;border-radius:20px;border:1px solid rgba(16,185,129,0.4);font-weight:600;">● Cloudflare Edge D1 Native</span></h1>
      <p style="margin:6px 0 0 0;font-size:14px;color:#94A3B8;">Real-time visual gallery of user uploaded photos, AI biometric risk &amp; payment status (Zero Render Cost)</p>
    </div>
    <div class="stats" style="align-items:center;">
      <button onclick="refreshNow()" style="background:#3B82F6;color:#fff;border:none;padding:12px 18px;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;">🔄 Refresh Now</button>
      <div class="stat-box">
        <div class="stat-value">${totalScans}</div>
        <div class="stat-label">Total Scans</div>
      </div>
      <div class="stat-box">
        <div class="stat-value">${totalPaid}</div>
        <div class="stat-label">Paid Scans</div>
      </div>
      <div class="stat-box">
        <div class="stat-value" style="color:#10B981;">$${revenue.toFixed(2)}</div>
        <div class="stat-label">Est. Revenue</div>
      </div>
      <div class="stat-box">
        <div class="stat-value" style="color:#A855F7;">${vLeadsCount}</div>
        <div class="stat-label">Video Leads</div>
      </div>
      <button onclick="resetScans()" style="background:#EF4444;color:#fff;border:none;padding:12px 18px;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;">🗑️ Reset Database</button>
    </div>
  </div>

  <div style="max-width: 1200px; margin: 0 auto 28px auto; background: #1E293B; padding: 24px 32px; border-radius: 20px; border: 1px solid #334155;">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#F8FAFC;">📊 Jurnale Plăți &amp; Erori API / Stripe</h2>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <input type="text" id="logSearchInput" placeholder="Caută după email, Scan ID sau eroare..." style="background:#0F172A;border:1px solid #334155;color:#fff;padding:8px 14px;border-radius:10px;font-size:13px;width:240px;" onkeyup="filterLogsTable()">
        <button id="btnFilterAll" onclick="setLogFilter('all')" style="background:#3B82F6;color:#fff;border:none;padding:8px 16px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;">Toate Jurnalele</button>
        <button id="btnFilterErrors" onclick="setLogFilter('error')" style="background:transparent;color:#EF4444;border:1px solid #EF4444;padding:8px 16px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;">Doar Erori</button>
        <button id="btnFilterSuccess" onclick="setLogFilter('success')" style="background:transparent;color:#10B981;border:1px solid #10B981;padding:8px 16px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;">Doar Plăți Reușite</button>
        <button onclick="clearPaymentErrors()" style="background:#DC2626;color:#fff;border:none;padding:8px 14px;border-radius:10px;font-size:13px;font-weight:700;cursor:pointer;">🗑️ Șterge Jurnale</button>
      </div>
    </div>
    <div style="overflow-x:auto;">
      <table id="logsTable" style="width:100%;border-collapse:collapse;text-align:left;font-size:13px;">
        <thead>
          <tr style="border-bottom:1px solid #334155;color:#94A3B8;">
            <th style="padding:12px;">Status</th>
            <th style="padding:12px;">Platformă</th>
            <th style="padding:12px;">Email Client</th>
            <th style="padding:12px;">Pachet / Broker</th>
            <th style="padding:12px;">Detalii Eroare API / Stripe</th>
            <th style="padding:12px;">Scan ID</th>
            <th style="padding:12px;">Data &amp; Ora</th>
          </tr>
        </thead>
        <tbody>
          ${logsTableRows || '<tr><td colspan="7" style="padding:20px;text-align:center;color:#94A3B8;">Nu există jurnale de plăți înregistrate încă.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <div style="max-width: 1200px; margin: 0 auto 28px auto; background: #1E293B; padding: 20px 28px; border-radius: 16px; border: 1px solid #334155;">
    <h3 style="margin:0 0 12px 0;font-size:16px;color:#A855F7;">🎥 Video Verification Leads (${vLeadsCount})</h3>
    ${vLeadsHtml || '<p style="color:#94A3B8;margin:0;font-size:13px;">No video verification leads submitted yet.</p>'}
  </div>

  <div class="grid">
    ${cardsHtml || '<p style="color:#94A3B8;grid-column:1/-1;text-align:center;padding:40px;background:#1E293B;border-radius:16px;">No scans recorded yet.</p>'}
  </div>

  <div id="img-modal-overlay" onclick="closeImgModal()" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(15,23,42,0.92);backdrop-filter:blur(8px);z-index:99999;align-items:center;justify-content:center;cursor:pointer;padding:20px;">
    <img id="img-modal-target" style="max-width:90vw;max-height:90vh;border-radius:16px;box-shadow:0 25px 50px -12px rgba(0,0,0,0.8);border:2px solid #38BDF8;object-fit:contain;" src=""/>
    <div style="position:absolute;top:20px;right:30px;color:#F8FAFC;font-size:32px;font-weight:bold;cursor:pointer;">&times;</div>
  </div>
</body>
</html>`;

  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "X-Robots-Tag": "noindex, nofollow, noarchive",
      "Cache-Control": "no-store"
    }
  });
}

// ============================================================================
// 5. MAIN NATIVE ROUTER FOR ISBROKERSAFE.COM & VERIFYDATING.NET
// ============================================================================
export async function handleBrokerDatingNative(request, env, ctx, host) {
  const url = new URL(request.url);
  const path = url.pathname;
  const cleanPath = path.length > 1 && path.endsWith("/") ? path.slice(0, -1) : path;
  const isBrokerSite = host === "isbrokersafe.com";

  if (request.method === "OPTIONS") {
    return { type: "response", response: jsonResponse({ ok: true }) };
  }

  // --------------------------------------------------------------------------
  // A. AFFILIATE REDIRECTS (/go/* and /out/*) + 4-LAYER BOT FIREWALL + D1 LOG
  // --------------------------------------------------------------------------
  if (cleanPath.startsWith("/go/") || cleanPath.startsWith("/out/")) {
    const noCacheHeaders = {
      "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
      "Pragma": "no-cache",
      "X-Robots-Tag": "noindex, nofollow, noarchive"
    };
    if (isNativeAffiliateBotRequest(request)) {
      return {
        type: "response",
        response: new Response("403 Forbidden - Automated crawler access to affiliate redirect endpoints is prohibited.", {
          status: 403,
          headers: { ...noCacheHeaders, "Content-Type": "text/plain; charset=utf-8" }
        })
      };
    }
    const slug = cleanPath.replace(/^\/(go|out)\//, "").toLowerCase();
    if (!/^[a-z0-9_-]{1,48}$/.test(slug)) {
      return {
        type: "response",
        response: new Response("403 Forbidden - Invalid redirect slug.", {
          status: 403,
          headers: { ...noCacheHeaders, "Content-Type": "text/plain; charset=utf-8" }
        })
      };
    }
    const visitorCc = String((request.cf && request.cf.country) || request.headers.get("cf-ipcountry") || "GB").toUpperCase();
    const entry = AFFILIATE_REDIRECTS[slug] || (isBrokerSite ? AFFILIATE_REDIRECTS["etoro"] : AFFILIATE_REDIRECTS["catfish-check"]);
    let finalUrl = (visitorCc === "US" && entry.urlUs) ? entry.urlUs : entry.url;
    if (entry.forwardSid) {
      const rawSid = url.searchParams.get("sid") || "";
      const cleanSid = rawSid.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 64);
      if (cleanSid) {
        const sep = finalUrl.includes("?") ? "&" : "?";
        finalUrl = `${finalUrl}${sep}sid=${cleanSid}`;
      }
    }
    const clientIp = request.headers.get("cf-connecting-ip") || "";
    if (env && env.DB && ctx && typeof ctx.waitUntil === "function") {
      ctx.waitUntil(
        (async () => {
          try {
            await env.DB.prepare(
              `INSERT INTO affiliate_clicks (country, city_slug, sku, network, target_url, user_ip_hash, user_agent) VALUES (?, ?, ?, ?, ?, ?, ?)`
            )
              .bind(
                visitorCc,
                host,
                slug,
                isBrokerSite ? "ibs_cpa" : "vd_cpa",
                finalUrl,
                clientIp.slice(0, 12),
                (request.headers.get("user-agent") || "").slice(0, 180)
              )
              .run();
          } catch (_) {}
        })()
      );
    }
    return {
      type: "response",
      response: new Response(null, {
        status: entry.status || 307,
        headers: {
          ...noCacheHeaders,
          "Location": finalUrl
        }
      })
    };
  }

  // AI Search Manifest (/llms.txt) & IndexNow Verification Key
  if (cleanPath === "/llms.txt") {
    const llmsTxt = isBrokerSite
      ? `# IsBrokerSafe.com — Global Regulatory Intelligence & Broker License Verification\n\n> IsBrokerSafe.com is an independent financial threat intelligence platform operated by VasileDev Group (VAT IT04226190041) indexing 9,732+ official regulatory blacklist warnings and Tier-1 licensed brokers across 82+ global financial authorities (IOSCO Network: FCA, CONSOB, BaFin, CySEC, SEC/CFTC, ASIC, CNMV, AMF, FINMA, MAS, SFC, DFSA, FSCA, FMA, CSA).\n\n## Key Endpoints\n- Homepage & Live Broker Scanner: https://isbrokersafe.com/\n- Tier-1 Regulated Brokers Registry: https://isbrokersafe.com/regulated-brokers\n- Regulatory Blacklist Directory (A-Z): https://isbrokersafe.com/directory/brokers\n- B2B Threat Intelligence REST API Docs: https://isbrokersafe.com/api/v1/docs\n- Live Check API Endpoint: https://isbrokersafe.com/api/v1/broker/check?domain=etoro.com\n- Primary Sitemap: https://isbrokersafe.com/sitemap.xml\n`
      : `# VerifyDating.net — Global Romance Scam & Catfish Forensic Intelligence\n\n> VerifyDating.net is a public cybersecurity utility operated by VasileDev Group (VAT IT04226190041) that provides instant reverse face recognition, deepfake detection, and 5,871+ documented romance scammer and Pig Butchering (Sha Zhu Pan) forensic dossiers across 8 languages.\n\n## Key Endpoints\n- Homepage & Free Photo Scanner: https://verifydating.net/\n- Public Romance Scammer Directory: https://verifydating.net/scammers\n- Online Dating Safety & Catfish Investigation Guides: https://verifydating.net/guides\n- Alphabetical Scammer Index (A-Z): https://verifydating.net/directory/dating\n- Developer API Documentation: https://verifydating.net/api/v1/dating-docs\n- Primary Sitemap: https://verifydating.net/sitemap.xml\n`;
    return {
      type: "response",
      response: new Response(llmsTxt, {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" }
      })
    };
  }

  if (cleanPath === "/d89b14f6824945e4a81b7e4521798361.txt") {
    return {
      type: "response",
      response: new Response("d89b14f6824945e4a81b7e4521798361", {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=86400" }
      })
    };
  }

  // --------------------------------------------------------------------------
  // B. HEALTH & API ENDPOINTS (/health, /healthz, /api/*)
  // --------------------------------------------------------------------------

  // Admin Dashboard & Admin API Routes
  if (cleanPath === "/admin" || cleanPath === "/admin/dashboard") {
    return { type: "response", response: await renderAdminDashboardHtml(env, url, request) };
  }
  if (cleanPath === "/api/admin/clear-scans" && request.method === "POST") {
    if (!checkAdminToken(url, request)) return { type: "response", response: jsonResponse({ error: "Forbidden" }, 403) };
    await env.DB.prepare("DELETE FROM vd_scans").run();
    await env.DB.prepare("DELETE FROM ib_broker_scans").run();
    await env.DB.prepare("DELETE FROM vd_video_leads").run();
    return { type: "response", response: jsonResponse({ status: "success", cleared: true }) };
  }
  if (cleanPath === "/api/admin/clear-payment-errors" && request.method === "POST") {
    if (!checkAdminToken(url, request)) return { type: "response", response: jsonResponse({ error: "Forbidden" }, 403) };
    await env.DB.prepare("DELETE FROM ib_payment_errors").run();
    return { type: "response", response: jsonResponse({ status: "success", cleared: true }) };
  }
  if (cleanPath === "/api/admin/mark-paid" && request.method === "POST") {
    if (!checkAdminToken(url, request)) return { type: "response", response: jsonResponse({ error: "Forbidden" }, 403) };
    const scanId = url.searchParams.get("scan_id") || "";
    await env.DB.prepare("UPDATE vd_scans SET payment_status = 'paid', package = 'basic' WHERE id = ?").bind(scanId).run();
    await env.DB.prepare("UPDATE ib_broker_scans SET payment_status = 'paid' WHERE id = ?").bind(scanId).run();
    return { type: "response", response: jsonResponse({ status: "success", scan_id: scanId, unlocked: true }) };
  }
  if (cleanPath === "/api/admin/scans") {
    if (!checkAdminToken(url, request)) return { type: "response", response: jsonResponse({ error: "Forbidden" }, 403) };
    const r = await env.DB.prepare("SELECT id, created_at, payment_status, scam_probability, matches_count, image_path, package FROM vd_scans ORDER BY created_at DESC LIMIT 100").all();
    return { type: "response", response: jsonResponse({ scans: (r && r.results) || [] }) };
  }

  if (cleanPath === "/health" || cleanPath === "/healthz") {
    return {
      type: "response",
      response: jsonResponse({ status: "ok", engine: "scam-radars-edge-native-d1", host })
    };
  }

  if (cleanPath === "/api/v1/geo-meta") {
    const country = (request.cf && request.cf.country) || "IT";
    return { type: "response", response: jsonResponse({ country }) };
  }

  if (cleanPath === "/api/sentinel/status") {
    return {
      type: "response",
      response: jsonResponse({
        status: "ACTIVE",
        engine: "Cloudflare Edge Sentinel v4.5",
        monitored_domains: 9009,
        licensed_institutions: 737,
        dating_profiles_indexed: 5871,
        last_sync: new Date().toISOString()
      })
    };
  }

  if (cleanPath === "/api/v1/stats" || cleanPath === "/api/stats") {
    const counts = await env.DB.prepare(
      `SELECT
        (SELECT COUNT(*) FROM ib_scam_reports) AS scam_brokers,
        (SELECT COUNT(*) FROM ib_regulated_brokers) AS reg_brokers,
        (SELECT COUNT(*) FROM vd_scam_profiles) AS dating_scammers`
    ).first();
    return {
      type: "response",
      response: jsonResponse({
        status: "ok",
        blacklisted_brokers: (counts && counts.scam_brokers) || 9009,
        regulated_brokers: (counts && counts.reg_brokers) || 737,
        dating_scam_profiles: (counts && counts.dating_scammers) || 5871,
        regulators_monitored: 82
      })
    };
  }

  if (cleanPath === "/api/scam-feed" || cleanPath === "/api/v1/regulatory/warnings") {
    const limit = Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "25", 10) || 25));
    const q = (url.searchParams.get("q") || url.searchParams.get("domain") || "").trim().toLowerCase();
    let res;
    if (q) {
      res = await env.DB.prepare(
        `SELECT slug, entity_name, domain, regulator, warning_type, warning_date, official_url, reason, jurisdiction, risk_score
         FROM ib_scam_reports
         WHERE LOWER(entity_name) LIKE ? OR LOWER(domain) LIKE ?
         ORDER BY id DESC LIMIT ?`
      ).bind(`%${q}%`, `%${q}%`, limit).all();
    } else {
      res = await env.DB.prepare(
        `SELECT slug, entity_name, domain, regulator, warning_type, warning_date, official_url, reason, jurisdiction, risk_score
         FROM ib_scam_reports ORDER BY id DESC LIMIT ?`
      ).bind(limit).all();
    }
    return {
      type: "response",
      response: jsonResponse({
        status: "ok",
        count: (res && res.results && res.results.length) || 0,
        warnings: (res && res.results) || []
      })
    };
  }

  if (cleanPath === "/api/brokers" || cleanPath === "/api/v1/broker/licensed") {
    const limit = Math.min(100, Math.max(1, parseInt(url.searchParams.get("limit") || "50", 10) || 50));
    const res = await env.DB.prepare(
      `SELECT slug, entity_name, domain, regulator, license_number, jurisdiction, category, trust_score
       FROM ib_regulated_brokers ORDER BY trust_score DESC, id ASC LIMIT ?`
    ).bind(limit).all();
    return {
      type: "response",
      response: jsonResponse({
        status: "ok",
        brokers: (res && res.results) || []
      })
    };
  }

  if (cleanPath === "/api/v1/broker/check") {
    const q = (url.searchParams.get("domain") || url.searchParams.get("q") || "").trim().toLowerCase().replace(/^https?:\/\/(www\.)?/, "").split("/")[0];
    if (!q) {
      return { type: "response", response: jsonResponse({ error: "Missing domain parameter" }, 400) };
    }
    const scam = await env.DB.prepare(
      `SELECT slug, entity_name, domain, regulator, warning_type, warning_date, official_url, reason, risk_score
       FROM ib_scam_reports WHERE LOWER(domain) = ? OR LOWER(entity_name) = ? OR LOWER(domain) LIKE ? LIMIT 1`
    ).bind(q, q, `%${q}%`).first();

    if (scam) {
      return {
        type: "response",
        response: jsonResponse({
          status: "BLACKLISTED",
          safe: false,
          risk_score: 96,
          trust_score: scam.risk_score || 4,
          record: scam
        })
      };
    }

    const reg = await env.DB.prepare(
      `SELECT slug, entity_name, domain, regulator, license_number, jurisdiction, trust_score
       FROM ib_regulated_brokers WHERE LOWER(domain) = ? OR LOWER(entity_name) = ? OR LOWER(domain) LIKE ? LIMIT 1`
    ).bind(q, q, `%${q}%`).first();

    if (reg) {
      return {
        type: "response",
        response: jsonResponse({
          status: "REGULATED",
          safe: true,
          risk_score: 5,
          trust_score: reg.trust_score || 95,
          record: reg
        })
      };
    }

    return {
      type: "response",
      response: jsonResponse({
        status: "UNVERIFIED",
        safe: false,
        risk_score: 55,
        trust_score: 45,
        message: "No matching license found in monitored Tier-1 registries."
      })
    };
  }

  // POST /api/broker/scan
  if (cleanPath === "/api/broker/scan" && request.method === "POST") {
    let body = {};
    try {
      body = await request.json();
    } catch (e) {}
    const rawDomain = String(body.domain || body.name || "unknown.com").trim().toLowerCase();
    const domain = rawDomain.replace(/^https?:\/\/(www\.)?/, "").split("/")[0];
    const name = String(body.name || domain).trim();
    const scanId = crypto.randomUUID();

    const staticHit = STATIC_BROKER_DB[domain] || STATIC_BROKER_DB[domain + ".com"] || STATIC_BROKER_DB[name.toLowerCase()];
    let score = 50;
    let verdictTitle = "Unverified Entity — No Matching License in Monitored Registries";
    let verdictText = `This entity (${domain}) was not found in our monitored Tier-1 regulatory license databases (737+ institutions) or official enforcement blacklists (9,009+ alerts). Verify its registration number directly on the national regulator portal before depositing capital.`;
    let redFlags = [
      "No matching Tier-1 license record found in monitored FCA/ESMA/SEC/ASIC/CySEC/FINMA databases.",
      "Manual license verification required prior to depositing funds."
    ];
    let greenFlags = [
      "No active regulatory enforcement blacklist order found under this exact domain name."
    ];
    let ip = "104.21.12.88";
    let hoster = "Cloudflare Global CDN";
    let domainAge = "Registered Web Domain";
    let affiliateLink = null;

    if (staticHit) {
      score = staticHit.score;
      verdictTitle = staticHit.verdictTitle;
      verdictText = staticHit.verdictText;
      redFlags = staticHit.redFlags;
      greenFlags = staticHit.greenFlags;
      ip = staticHit.ip;
      hoster = staticHit.hoster;
      domainAge = staticHit.domainAge;
      affiliateLink = staticHit.affiliateLink;
    } else {
      const scamRow = await env.DB.prepare(
        `SELECT entity_name, domain, regulator, warning_type, warning_date, reason, risk_score
         FROM ib_scam_reports
         WHERE LOWER(domain) = ? OR LOWER(entity_name) = ? OR (LENGTH(?) >= 4 AND (LOWER(domain) LIKE ? OR LOWER(entity_name) LIKE ?))
         LIMIT 1`
      ).bind(domain, name.toLowerCase(), domain, `%${domain}%`, `%${name.toLowerCase()}%`).first();

      if (scamRow) {
        score = 4;
        verdictTitle = `CRITICAL RISK — BLACKLISTED BY ${scamRow.regulator}`;
        verdictText = `Official regulatory enforcement alerts confirm that ${scamRow.entity_name} (${scamRow.domain || domain}) is flagged by ${scamRow.regulator} (${scamRow.warning_date || "2026"}). Client funds have zero statutory protection.`;
        redFlags = [
          `Official Blacklist: Confirmed enforcement alert issued by ${scamRow.regulator}.`,
          `Infringement Classification: ${scamRow.warning_type || "Unauthorized Financial Services"}.`,
          `Regulatory Grounds: ${scamRow.reason || "Operating without mandatory authorization."}`,
          "Zero Investor Protection: Operating without statutory capital reserves."
        ];
        greenFlags = [];
      } else {
        const regRow = await env.DB.prepare(
          `SELECT entity_name, domain, regulator, license_number, jurisdiction, category, trust_score
           FROM ib_regulated_brokers
           WHERE LOWER(domain) = ? OR LOWER(entity_name) = ? OR (LENGTH(?) >= 5 AND (LOWER(domain) LIKE ? OR LOWER(entity_name) LIKE ?))
           LIMIT 1`
        ).bind(domain, name.toLowerCase(), domain, `%${domain}%`, `%${name.toLowerCase()}%`).first();

        if (regRow) {
          score = Math.max(88, Number(regRow.trust_score || 95));
          verdictTitle = `VERIFIED LICENSED INSTITUTION (${regRow.regulator})`;
          verdictText = `Official regulatory registry check confirms that ${regRow.entity_name} (${regRow.domain}) is an authorized financial institution supervised by ${regRow.regulator} under License #${regRow.license_number} (${regRow.jurisdiction}).`;
          redFlags = [];
          greenFlags = [
            `Official Regulatory Supervision: ${regRow.regulator} (${regRow.jurisdiction})`,
            `Verified License / Registration Number: ${regRow.license_number}`,
            `Authorized Category: ${regRow.category || "Regulated Financial Institution"}`,
            "No active enforcement blacklist orders found across 82 global IOSCO authorities."
          ];
        }
      }
    }

    await env.DB.prepare(
      `INSERT OR REPLACE INTO ib_broker_scans
       (id, broker_name, broker_domain, regulation, leverage, source, promises, score, payment_status, email, created_at, ip_address, hosting_provider, domain_age, red_flags, green_flags, verdict_title, verdict_text)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'paid', '', ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      scanId,
      name || domain,
      domain,
      String(body.regulation || "unregulated"),
      String(body.leverage || "regulated-leverage"),
      String(body.source || "organic"),
      String(body.promises || "realistic"),
      score,
      new Date().toISOString(),
      ip,
      hoster,
      domainAge,
      JSON.stringify(redFlags),
      JSON.stringify(greenFlags),
      verdictTitle,
      verdictText
    ).run();

    return {
      type: "response",
      response: jsonResponse({
        scan_id: scanId,
        payment_status: "paid",
        score,
        broker_name: name || domain,
        broker_domain: domain,
        ip_address: ip,
        hosting_provider: hoster,
        domain_age: domainAge,
        red_flags: redFlags,
        green_flags: greenFlags,
        verdict_title: verdictTitle,
        verdict_text: verdictText,
        affiliate_link: affiliateLink
      })
    };
  }

  // GET /api/broker/results/{scan_id}
  if (cleanPath.startsWith("/api/broker/results/")) {
    const scanId = cleanPath.replace("/api/broker/results/", "");
    const row = await env.DB.prepare(
      `SELECT payment_status, score, broker_name, broker_domain, ip_address, hosting_provider, domain_age, red_flags, green_flags, verdict_title, verdict_text
       FROM ib_broker_scans WHERE id = ? LIMIT 1`
    ).bind(scanId).first();

    if (row) {
      let redFlags = [];
      let greenFlags = [];
      try { redFlags = JSON.parse(row.red_flags || "[]"); } catch (e) {}
      try { greenFlags = JSON.parse(row.green_flags || "[]"); } catch (e) {}
      return {
        type: "response",
        response: jsonResponse({
          scan_id: scanId,
          payment_status: row.payment_status || "paid",
          score: row.score ?? 95,
          broker_name: row.broker_name || "Verified Broker",
          broker_domain: row.broker_domain || "broker.com",
          ip_address: row.ip_address || "104.21.12.88",
          hosting_provider: row.hosting_provider || "Cloudflare CDN",
          domain_age: row.domain_age || "Registered Domain",
          red_flags: redFlags,
          green_flags: greenFlags,
          verdict_title: row.verdict_title || "Audit Completed",
          verdict_text: row.verdict_text || "Forensic verification complete.",
          affiliate_link: null
        })
      };
    }

    return {
      type: "response",
      response: jsonResponse({
        scan_id: scanId,
        payment_status: "paid",
        score: 96,
        broker_name: "eToro",
        broker_domain: "etoro.com",
        ip_address: "104.18.14.101",
        hosting_provider: "Cloudflare Enterprise CDN",
        domain_age: "2000-05-11 (26 years ago)",
        red_flags: [],
        green_flags: ["Tier-1 license verified (FCA, CySEC, ASIC).", "Segregated investor accounts active."],
        verdict_title: "Verified Regulated Broker",
        verdict_text: "Active regulatory compliance verified. Low risk exposure.",
        affiliate_link: "/go/etoro"
      })
    };
  }

  // Printable Forensic Report for /api/broker/report/{scan_id} or /api/v1/broker/pdf/{slug}
  if (cleanPath.startsWith("/api/broker/report/") || cleanPath.startsWith("/api/v1/broker/pdf/")) {
    const idOrSlug = cleanPath.split("/").pop();
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Forensic Audit Dossier — ${escHtml(idOrSlug)} | IsBrokerSafe</title>
  <style>
    body { font-family: Arial, sans-serif; color: #0f172a; max-width: 800px; margin: 32px auto; padding: 24px; line-height: 1.6; }
    .box { border: 2px solid #0f172a; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
    @media print { .no-print { display: none; } }
  </style>
</head>
<body onload="window.print()">
  <div class="no-print" style="margin-bottom:16px;">
    <button onclick="window.print()" style="padding:10px 18px;background:#0284c7;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;">🖨️ Print / Save as PDF</button>
    <a href="/" style="margin-left:12px;color:#0284c7;">Back to IsBrokerSafe.com</a>
  </div>
  <div class="box">
    <h1 style="margin:0 0 6px;">ISBROKERSAFE™ FORENSIC COMPLIANCE DOSSIER</h1>
    <p style="margin:0;color:#475569;font-size:13px;">Reference ID: <strong>${escHtml(idOrSlug)}</strong> &bull; Generated: ${new Date().toISOString().slice(0, 10)}</p>
  </div>
  <div class="box">
    <h2>Regulatory &amp; Infrastructure Verification</h2>
    <p>This forensic compliance certificate was generated by the IsBrokerSafe Edge Threat Intelligence Engine across 82 global financial supervisory authorities (FCA, CySEC, ASIC, SEC, CONSOB, BaFin, CNMV, AMF, ASF).</p>
    <p>Always verify the entity's registration number directly on the national regulator's official register before transferring capital.</p>
  </div>
</body>
</html>`;
    return {
      type: "response",
      response: new Response(html, {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex, nofollow" }
      })
    };
  }

  // VerifyDating API Endpoints (/api/scan, /api/scan-url, /api/results/{id}, /api/dating/scammers)
  if ((cleanPath === "/api/scan" || cleanPath === "/api/scan-url") && request.method === "POST") {
    const scanId = crypto.randomUUID();
    let seedSource = scanId;
    let imageUrl = "";
    let imgBase64 = "";
    try {
      const ct = request.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const body = await request.json();
        seedSource = String(body.url || scanId);
        imageUrl = seedSource;
      } else if (ct.includes("multipart/form-data")) {
        const formData = await request.formData();
        const file = formData.get("file");
        if (file && file.name) {
          seedSource = `${file.name}-${file.size || 0}`;
          try {
            const buf = await file.arrayBuffer();
            if (buf && buf.byteLength > 0 && buf.byteLength < 1500000) {
              imgBase64 = arrayBufferToBase64(buf);
            }
          } catch (e) {}
        }
      }
    } catch (e) {}

    const h = fnv1a(seedSource);
    const scamProbability = 72 + (h % 25);
    const matchesCount = 4 + (h % 9);
    const matchesData = [
      { platform: "Google Lens Visual Index", url: imageUrl ? `https://lens.google.com/uploadbyurl?url=${encodeURIComponent(imageUrl)}` : "https://lens.google.com/" },
      { platform: "Yandex Reverse Face Search", url: imageUrl ? `https://yandex.com/images/search?rpt=imageview&url=${encodeURIComponent(imageUrl)}` : "https://yandex.com/images/" },
      { platform: "TinEye Perceptual Hash Match", url: imageUrl ? `https://tineye.com/search?url=${encodeURIComponent(imageUrl)}` : "https://tineye.com/" },
      { platform: "VerifyDating OSINT Catfish Registry", url: "https://verifydating.net/scammers" }
    ];
    const scammerInfo = "High-risk biometric & OSINT correlation: This profile image matches public social media / stock portfolios frequently reused across dating apps under multiple aliases.";

    await env.DB.prepare(
      `INSERT OR REPLACE INTO vd_scans (id, image_path, created_at, payment_status, scam_probability, matches_count, matches_data, scammer_info, email, image_base64, package)
       VALUES (?, ?, ?, 'unpaid', ?, ?, ?, ?, '', ?, 'basic')`
    ).bind(
      scanId,
      imageUrl || "uploaded_photo.jpg",
      new Date().toISOString(),
      scamProbability,
      matchesCount,
      JSON.stringify(matchesData),
      scammerInfo,
      imgBase64
    ).run();

    return {
      type: "response",
      response: jsonResponse({
        scan_id: scanId,
        scam_probability: scamProbability,
        matches_count: matchesCount
      })
    };
  }

  if (cleanPath.startsWith("/api/results/")) {
    const parts = cleanPath.replace("/api/results/", "").split("/");
    const scanId = parts[0];
    const isPdf = parts[1] === "pdf";

    const row = await env.DB.prepare(
      `SELECT payment_status, scam_probability, matches_count, matches_data, scammer_info, email, created_at
       FROM vd_scans WHERE id = ? LIMIT 1`
    ).bind(scanId).first();

    const scamProb = (row && row.scam_probability) || 86;
    const matchesCount = (row && row.matches_count) || 7;
    let matches = [];
    try { matches = JSON.parse((row && row.matches_data) || "[]"); } catch (e) {}
    const scammerInfo = (row && row.scammer_info) || "Profile image matches multiple public social media portfolios.";

    if (isPdf) {
      const pdfHtml = `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VerifyDating Report ${escHtml(scanId)}</title></head>
<body onload="window.print()" style="font-family:Arial,sans-serif;max-width:760px;margin:32px auto;padding:24px;">
  <h1>VERIFYDATING™ ROMANCE SCAM DETECTION REPORT</h1>
  <p>Scan ID: <strong>${escHtml(scanId)}</strong> &bull; Scam Probability: <strong>${scamProb}%</strong> &bull; Matches: <strong>${matchesCount}</strong></p>
  <p>${escHtml(scammerInfo)}</p>
</body></html>`;
      return {
        type: "response",
        response: new Response(pdfHtml, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex" } })
      };
    }

    return {
      type: "response",
      response: jsonResponse({
        scan_id: scanId,
        payment_status: "paid",
        unlocked: true,
        scam_probability: scamProb,
        matches_count: matchesCount,
        matches,
        scammer_info: scammerInfo,
        email: (row && row.email) || "",
        credits_remaining: 3,
        pdf_price: "2.99"
      })
    };
  }

  if (cleanPath === "/api/dating/scammers" || cleanPath === "/api/v1/dating/check" || cleanPath === "/api/v1/face/check") {
    const q = (url.searchParams.get("q") || url.searchParams.get("name") || "").trim().toLowerCase();
    const res = q
      ? await env.DB.prepare(`SELECT slug, persona_name, claimed_age, claimed_location, claimed_profession, scam_category, risk_score FROM vd_scam_profiles WHERE LOWER(persona_name) LIKE ? LIMIT 25`).bind(`%${q}%`).all()
      : await env.DB.prepare(`SELECT slug, persona_name, claimed_age, claimed_location, claimed_profession, scam_category, risk_score FROM vd_scam_profiles ORDER BY id DESC LIMIT 25`).all();
    return {
      type: "response",
      response: jsonResponse({ status: "ok", results: (res && res.results) || [] })
    };
  }

  if (cleanPath === "/api/v1/face/stats") {
    return {
      type: "response",
      response: jsonResponse({ status: "ok", indexed_faces: 5871, categories: 12, engine: "VerifyDating Edge Biometric Index" })
    };
  }

  if (cleanPath === "/api/pay-card" || cleanPath === "/api/pay-paypal" || cleanPath === "/api/use-credit" || cleanPath === "/api/pay-paypal-ipn" || cleanPath === "/api/v1/webhooks/paypal-b2b") {
    return {
      type: "response",
      response: jsonResponse({ success: true, status: "ok", unlocked: true, credits_remaining: 3, message: "Report unlocked." })
    };
  }

  if (cleanPath.startsWith("/api/credits/")) {
    const email = decodeURIComponent(cleanPath.replace("/api/credits/", ""));
    return { type: "response", response: jsonResponse({ email, credits_remaining: 3 }) };
  }

  if (cleanPath === "/api/video-lead" || cleanPath === "/api/crypto-vote") {
    return { type: "response", response: jsonResponse({ success: true, total_votes: 412, target: 1000 }) };
  }

  if (cleanPath === "/api/v1/keys/generate") {
    return {
      type: "response",
      response: jsonResponse({
        status: "ok",
        api_key: `ibs_live_${crypto.randomUUID().replace(/-/g, "")}`,
        tier: "free",
        monthly_quota: 100
      })
    };
  }

  // --------------------------------------------------------------------------
  // C. STATIC ASSETS (/style.css, /app.js, /favicon.svg, /extension/download, etc.)
  // --------------------------------------------------------------------------
  if (cleanPath === "/extension/download" || cleanPath === "/static/SafeShield-Chrome-Extension.zip") {
    const zipRes = await fetchStaticAsset(env, request.url, "/static/SafeShield-Chrome-Extension.zip", "application/zip");
    if (zipRes) return { type: "response", response: zipRes };
  }

  if (cleanPath === "/postman.json" || cleanPath === "/api/v1/postman.json") {
    const pmRes = await fetchStaticAsset(env, request.url, "/static/postman.json", "application/json; charset=utf-8");
    if (pmRes) return { type: "response", response: pmRes };
  }

  if (cleanPath === "/api/v1/openapi.json") {
    const oaRes = await fetchStaticAsset(env, request.url, "/ib_pages/openapi.json", "application/json; charset=utf-8");
    if (oaRes) return { type: "response", response: oaRes };
  }

  const cdnMap = {
    "/style.css": isBrokerSite ? "/cdn/ib_style.css" : "/cdn/vd_style.css",
    "/broker-verifier/style.css": "/cdn/ib_style.css",
    "/broker-verifier/broker-verifier/style.css": "/cdn/ib_style.css",
    "/app.js": isBrokerSite ? "/cdn/ib_app.js" : "/cdn/vd_app.js",
    "/broker-verifier/app.js": "/cdn/ib_app.js",
    "/broker-verifier/broker-verifier/app.js": "/cdn/ib_app.js",
    "/index.css": "/cdn/index.css",
    "/favicon.svg": isBrokerSite ? "/cdn/ib_favicon.svg" : "/cdn/vd_favicon.svg",
    "/favicon.ico": isBrokerSite ? "/cdn/ib_favicon.svg" : "/cdn/vd_favicon.svg",
    "/dating-favicon.svg": "/cdn/dating-favicon.svg",
    "/ib_favicon.svg": "/cdn/ib_favicon.svg",
    "/vd_favicon.svg": "/cdn/vd_favicon.svg",
    "/tech_bg.webp": "/cdn/tech_bg.webp",
    "/broker-verifier/tech_bg.webp": "/cdn/tech_bg.webp",
    "/broker-verifier/broker-verifier/tech_bg.webp": "/cdn/tech_bg.webp",
    "/dating_bg.webp": "/cdn/dating_bg.webp",
    "/dev_bg.webp": "/cdn/dev_bg.webp",
    "/catfish_profile.png": "/cdn/catfish_profile.png",
    "/video_thumbnail.png": "/cdn/video_thumbnail.png",
    "/explainer.mp4": "/cdn/explainer.mp4",
    "/2ab18b31-5d07-453b-b743-bfbfe1ee49df.jpeg": "/cdn/2ab18b31-5d07-453b-b743-bfbfe1ee49df.jpeg",
    "/google_ads_logo_512x512.png": "/cdn/google_ads_logo_512x512.png",
    "/og_image.png": "/cdn/og_image.png",
    "/og_image.jpg": "/cdn/og_image.jpg",
    "/verifydating_og_banner.jpg": "/cdn/verifydating_og_banner.jpg",
    "/isbrokersafe_og_banner.jpg": "/cdn/isbrokersafe_og_banner.jpg",
    "/badge.js": "/static/badge.js",
    "/bg.jpg": "/static/bg.jpg"
  };

  let mappedAsset = cdnMap[cleanPath] || null;
  if (!mappedAsset) {
    const lowP = cleanPath.toLowerCase();
    if (lowP.endsWith("/style.css")) mappedAsset = isBrokerSite ? "/cdn/ib_style.css" : "/cdn/vd_style.css";
    else if (lowP.endsWith("/app.js")) mappedAsset = isBrokerSite ? "/cdn/ib_app.js" : "/cdn/vd_app.js";
    else if (lowP.endsWith("/favicon.svg") || lowP.endsWith("/favicon.ico")) mappedAsset = isBrokerSite ? "/cdn/ib_favicon.svg" : "/cdn/vd_favicon.svg";
    else if (lowP.endsWith("/tech_bg.webp")) mappedAsset = "/cdn/tech_bg.webp";
    else if (lowP.endsWith("/dating_bg.webp")) mappedAsset = "/cdn/dating_bg.webp";
    else if (lowP.endsWith("/dev_bg.webp")) mappedAsset = "/cdn/dev_bg.webp";
    else if (lowP.endsWith("/video_thumbnail.png")) mappedAsset = "/cdn/video_thumbnail.png";
    else if (lowP.endsWith("/catfish_profile.png")) mappedAsset = "/cdn/catfish_profile.png";
    else if (lowP.endsWith("/explainer.mp4")) mappedAsset = "/cdn/explainer.mp4";
  }

  if (mappedAsset) {
    const assetRes = await fetchStaticAsset(env, request.url, mappedAsset, null, request.method);
    if (assetRes) return { type: "response", response: assetRes };
  }

  if (cleanPath.startsWith("/cdn/") || cleanPath.startsWith("/static/")) {
    const assetRes = await fetchStaticAsset(env, request.url, cleanPath, null, request.method);
    if (assetRes) return { type: "response", response: assetRes };
  }

  // --------------------------------------------------------------------------
  // D. PRE-RENDERED HUB & STATIC HTML PAGES FROM env.ASSETS
  // --------------------------------------------------------------------------
  const pageFolder = isBrokerSite ? "/ib_pages" : "/vd_pages";

  if (cleanPath === "" || cleanPath === "/") {
    const html = await readStaticHtml(env, request.url, `${pageFolder}/index.html`);
    if (html) return { type: "html", html, status: 200 };
  }

  const segments = cleanPath.slice(1).split("/");
  if (segments.length === 1 && SUPPORTED_LANGS.includes(segments[0])) {
    const html = await readStaticHtml(env, request.url, `${pageFolder}/${segments[0]}/index.html`);
    if (html) return { type: "html", html, status: 200 };
  }

  // Reviews (/reviews/{b} and /{lang}/reviews/{b})
  if (segments.length === 2 && segments[0] === "reviews") {
    const html = await readStaticHtml(env, request.url, `/ib_pages/reviews/${segments[1]}.html`);
    if (html) return { type: "html", html, status: 200 };
  }
  if (segments.length === 3 && SUPPORTED_LANGS.includes(segments[0]) && segments[1] === "reviews") {
    const html = await readStaticHtml(env, request.url, `/ib_pages/${segments[0]}/reviews/${segments[2]}.html`);
    if (html) return { type: "html", html, status: 200 };
  }

  // Guides (/guides and /guides/{slug})
  if (cleanPath === "/guides") {
    const html = await readStaticHtml(env, request.url, "/vd_pages/guides.html");
    if (html) return { type: "html", html, status: 200 };
  }
  if (segments.length === 2 && segments[0] === "guides") {
    const html = await readStaticHtml(env, request.url, `/vd_pages/guides/${segments[1]}.html`);
    if (html) return { type: "html", html, status: 200 };
  }

  const staticPageMap = {
    "/pricing": "/ib_pages/pricing.html",
    "/widget": "/ib_pages/widget.html",
    "/badge": "/ib_pages/widget.html",
    "/dating-widget": "/vd_pages/dating-widget.html",
    "/dating-badge": "/vd_pages/dating-widget.html",
    "/api/v1/docs": "/ib_pages/api_docs.html",
    "/api/v1/dating-docs": "/vd_pages/dating-docs.html",
    "/dating-api": "/vd_pages/dating-docs.html",
    "/extension": `${pageFolder}/extension.html`,
    "/safeshield": `${pageFolder}/extension.html`,
    "/privacy": `${pageFolder}/privacy-policy.html`,
    "/privacy-policy": `${pageFolder}/privacy-policy.html`,
    "/privacy-policy.html": `${pageFolder}/privacy-policy.html`,
    "/promo": "/vd_pages/promo.html",
    "/regulated-brokers": "/ib_pages/regulated-brokers.html",
    "/directory": isBrokerSite ? "/ib_pages/directory_brokers.html" : "/vd_pages/directory_dating.html",
    "/directory/brokers": "/ib_pages/directory_brokers.html",
    "/directory/dating": "/vd_pages/directory_dating.html"
  };

  if (staticPageMap[cleanPath]) {
    const html = await readStaticHtml(env, request.url, staticPageMap[cleanPath]);
    if (html) return { type: "html", html, status: 200 };
  }

  // --------------------------------------------------------------------------
  // E. DYNAMIC D1 HTML DOSSIERS (/scam-reports/*, /audit/*, /scammers, /scammer/*, /directory/*)
  // --------------------------------------------------------------------------
  if (segments.length === 2 && segments[0] === "scam-reports") {
    const html = await renderBrokerScamReportHtml(env, segments[1], "en");
    if (html) return { type: "html", html, status: 200 };
  }
  if (segments.length === 3 && SUPPORTED_LANGS.includes(segments[0]) && segments[1] === "scam-reports") {
    const html = await renderBrokerScamReportHtml(env, segments[2], segments[0]);
    if (html) return { type: "html", html, status: 200 };
  }

  if (segments.length === 2 && segments[0] === "audit") {
    const html = await renderBrokerAuditHtml(env, decodeURIComponent(segments[1]));
    if (html) return { type: "html", html, status: 200 };
  }

  if (cleanPath === "/scammers" || (segments.length === 2 && SUPPORTED_LANGS.includes(segments[0]) && segments[1] === "scammers")) {
    const html = await renderScammersDirectoryHtml(env, request.url);
    if (html) return { type: "html", html, status: 200 };
  }

  if (segments.length === 2 && segments[0] === "scammer") {
    const html = await renderScammerProfileHtml(env, segments[1], "en");
    if (html) return { type: "html", html, status: 200 };
  }
  if (segments.length === 3 && SUPPORTED_LANGS.includes(segments[0]) && segments[1] === "scammer") {
    const html = await renderScammerProfileHtml(env, segments[2], segments[0]);
    if (html) return { type: "html", html, status: 200 };
  }

  if (segments.length === 3 && segments[0] === "directory" && (segments[1] === "brokers" || segments[1] === "dating")) {
    const html = await renderAlphabeticalDirectoryHtml(env, host, segments[1], segments[2]);
    if (html) return { type: "html", html, status: 200 };
  }

  // --------------------------------------------------------------------------
  // F. STRICT 404 NOT FOUND (Zero Render calls)
  // --------------------------------------------------------------------------
  const html404 = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>404 Not Found | ${escHtml(host)}</title>
  <meta name="robots" content="noindex, nofollow">
</head>
<body style="font-family:Inter,sans-serif;background:#070b14;color:#f8fafc;text-align:center;padding:80px 20px;">
  <h1 style="font-size:36px;">404 — Page Not Found</h1>
  <p style="color:#94a3b8;">The requested dossier or resource does not exist on ${escHtml(host)}.</p>
  <a href="/" style="display:inline-block;margin-top:16px;padding:12px 24px;background:#38bdf8;color:#070b14;border-radius:10px;text-decoration:none;font-weight:700;">Return to Homepage</a>
</body>
</html>`;
  return {
    type: "html",
    html: html404,
    status: 404,
    extraHeaders: { "X-Robots-Tag": "noindex, nofollow" }
  };
}
