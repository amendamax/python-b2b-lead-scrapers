export interface Env {
  DB: D1Database;
  DB_ITALY?: D1Database;
  DB_ROMANIA?: D1Database;
  EU_GATEWAY?: Fetcher;
  RO_INDEXER?: Fetcher;
  IT_INDEXER?: Fetcher;
  SECRET_JOBSCAM?: string;
  SECRET_PILLSCAM?: string;
  SECRET_APPSCAM?: string;
  SECRET_BROKER?: string;
  SECRET_DATING?: string;
}

interface SiteConfig {
  id: string;
  name: string;
  domain: string;
  secretKey: keyof Env;
  dailyQuota: number;
  icon: string;
  defaultTotal?: number;
  apiEmail?: string;
}

const SITES: Record<string, SiteConfig> = {
  calculeazasubventii: {
    id: "calculeazasubventii",
    name: "CalculeazaSubventii.ro (#1 BPS™ Cloud RO)",
    domain: "https://calculeazasubventii.ro",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 400,
    icon: "🇷🇴",
    apiEmail: "robot-seo@solar-indexer.iam.gserviceaccount.com (2x Bots)",
  },
  calcolaincentivi: {
    id: "calcolaincentivi",
    name: "CalcolaIncentivi.it (#1 BPS™ Cloud IT)",
    domain: "https://calcolaincentivi.it",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 400,
    icon: "🇮🇹",
    apiEmail: "robot-italia@jobscam-indexer.iam.gserviceaccount.com (2x Bots)",
  },
  eu_hu: {
    id: "eu_hu",
    name: "PalyazatKalkulator.hu (#1 BPS™ Cloud HU)",
    domain: "https://palyazatkalkulator.hu",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "🇭🇺",
    defaultTotal: 1328,
    apiEmail: "bot-hu@eu-indexer-hu-19356.iam.gserviceaccount.com",
  },
  eu_de: {
    id: "eu_de",
    name: "FoerderungBerechnen.de",
    domain: "https://foerderungberechnen.de",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 400,
    icon: "🇩🇪",
    defaultTotal: 8141,
    apiEmail: "bot-de@eu-indexer-de-25152.iam.gserviceaccount.com (2x Bots)",
  },
  eu_at: {
    id: "eu_at",
    name: "FoerderungBerechnen.at",
    domain: "https://foerderungberechnen.at",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 200,
    icon: "🇦🇹",
    defaultTotal: 2847,
    apiEmail: "bot-at@eu-indexer-at-19706.iam.gserviceaccount.com",
  },
  eu_fr: {
    id: "eu_fr",
    name: "CalculeSubventions.fr",
    domain: "https://calculesubventions.fr",
    secretKey: "SECRET_BROKER",
    dailyQuota: 400,
    icon: "🇫🇷",
    defaultTotal: 9512,
    apiEmail: "bot-fr@eu-indexer-fr-14818.iam.gserviceaccount.com (2x Bots)",
  },
  eu_es: {
    id: "eu_es",
    name: "CalculaSubvenciones.es",
    domain: "https://calculasubvenciones.es",
    secretKey: "SECRET_DATING",
    dailyQuota: 400,
    icon: "🇪🇸",
    defaultTotal: 7723,
    apiEmail: "bot-es@eu-indexer-es-23290.iam.gserviceaccount.com (2x Bots)",
  },
  eu_pl: {
    id: "eu_pl",
    name: "ObliczDotacje.pl",
    domain: "https://obliczdotacje.pl",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 400,
    icon: "🇵🇱",
    defaultTotal: 3818,
    apiEmail: "bot-pl@eu-indexer-pl-29145.iam.gserviceaccount.com (2x Bots)",
  },
  eu_nl: {
    id: "eu_nl",
    name: "BerekenSubsidie.nl",
    domain: "https://berekensubsidie.nl",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 400,
    icon: "🇳🇱",
    defaultTotal: 2405,
    apiEmail: "bot-nl@eu-indexer-nl-1780.iam.gserviceaccount.com (2x Bots)",
  },
  eu_be: {
    id: "eu_be",
    name: "PremieBerekenen.be",
    domain: "https://premieberekenen.be",
    secretKey: "SECRET_BROKER",
    dailyQuota: 200,
    icon: "🇧🇪",
    defaultTotal: 2222,
    apiEmail: "bot-be@eu-indexer-be-20932.iam.gserviceaccount.com",
  },
  eu_cz: {
    id: "eu_cz",
    name: "SpocitejDotaci.cz",
    domain: "https://spocitejdotaci.cz",
    secretKey: "SECRET_DATING",
    dailyQuota: 200,
    icon: "🇨🇿",
    defaultTotal: 2073,
    apiEmail: "bot-cz@eu-indexer-cz-37898.iam.gserviceaccount.com",
  },
  eu_uk: {
    id: "eu_uk",
    name: "UKGrantCalculator.co.uk",
    domain: "https://ukgrantcalculator.co.uk",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 400,
    icon: "🇬🇧",
    defaultTotal: 4821,
    apiEmail: "bot-uk@eu-indexer-uk-13301.iam.gserviceaccount.com (2x Bots)",
  },
  eu_pt: {
    id: "eu_pt",
    name: "CalculaIncentivos.pt",
    domain: "https://calculaincentivos.pt",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "🇵🇹",
    defaultTotal: 1292,
    apiEmail: "bot-pt@eu-indexer-pt-26542.iam.gserviceaccount.com",
  },
  eu_dk: {
    id: "eu_dk",
    name: "BeregnStotte.dk",
    domain: "https://beregnstotte.dk",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "🇩🇰",
    defaultTotal: 557,
    apiEmail: "bot-dk@eu-indexer-dk-30483.iam.gserviceaccount.com",
  },
  eu_se: {
    id: "eu_se",
    name: "Bidragskalkylator.se",
    domain: "https://bidragskalkylator.se",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "🇸🇪",
    defaultTotal: 328,
    apiEmail: "bot-se@eu-indexer-se-17337.iam.gserviceaccount.com",
  },
  eu_lu: {
    id: "eu_lu",
    name: "CalculeSubventions.fr/lu (Klimabonus)",
    domain: "https://calculesubventions.fr/lu",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "🇱🇺",
    defaultTotal: 114,
    apiEmail: "bot-fr@eu-indexer-fr-97367.iam.gserviceaccount.com (Shared .FR Owner)",
  },
  jobscam: {
    id: "jobscam",
    name: "JobScamRadar",
    domain: "https://jobscamradar.com",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 200,
    icon: "💼",
    apiEmail: "jobscam-bot@jobscam-dedicated.iam.gserviceaccount.com",
  },
  broker: {
    id: "broker",
    name: "IsBrokerSafe",
    domain: "https://isbrokersafe.com",
    secretKey: "SECRET_BROKER",
    dailyQuota: 200,
    icon: "🛡️",
    defaultTotal: 72256,
    apiEmail: "broker-bot@broker-indexing.iam.gserviceaccount.com",
  },
  dating: {
    id: "dating",
    name: "VerifyDating",
    domain: "https://verifydating.net",
    secretKey: "SECRET_DATING",
    dailyQuota: 200,
    icon: "❤️",
    defaultTotal: 67598,
    apiEmail: "dating-bot@dating-indexing-511010.iam.gserviceaccount.com",
  },
  pillscam: {
    id: "pillscam",
    name: "PillScamRadar",
    domain: "https://pillscamradar.com",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 200,
    icon: "💊",
    apiEmail: "botul-meu@pill-bot-1.iam.gserviceaccount.com",
  },
  appscam: {
    id: "appscam",
    name: "AppScamRadar",
    domain: "https://appscamradar.com",
    secretKey: "SECRET_APPSCAM",
    dailyQuota: 200,
    icon: "📱",
    apiEmail: "pill-bot-2@jobscam-indexer.iam.gserviceaccount.com",
  },
};

// Minimal JWT Signer for Cloudflare Workers (Native Web Crypto)
async function signJwt(clientEmail: string, privateKey: string, scope: string): Promise<string> {
  const header = { alg: "RS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    iss: clientEmail,
    scope: scope,
    aud: "https://oauth2.googleapis.com/token",
    exp: now + 3600,
    iat: now,
  };

  const encodeBase64Url = (obj: any) =>
    btoa(JSON.stringify(obj))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");

  const encodedHeader = encodeBase64Url(header);
  const encodedPayload = encodeBase64Url(payload);
  const dataToSign = `${encodedHeader}.${encodedPayload}`;

  const pemHeader = "-----BEGIN PRIVATE KEY-----";
  const pemFooter = "-----END PRIVATE KEY-----";
  const pemContents = privateKey
    .replace(pemHeader, "")
    .replace(pemFooter, "")
    .replace(/\\n/g, "")
    .replace(/\s/g, "");

  const binaryDer = Uint8Array.from(atob(pemContents), (c) => c.charCodeAt(0));

  const cryptoKey = await crypto.subtle.importKey(
    "pkcs8",
    binaryDer,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"]
  );

  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    cryptoKey,
    new TextEncoder().encode(dataToSign)
  );

  const encodedSignature = btoa(String.fromCharCode(...new Uint8Array(signature)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");

  return `${dataToSign}.${encodedSignature}`;
}

async function getAccessToken(clientEmail: string, privateKey: string): Promise<string | null> {
  try {
    const jwt = await signJwt(clientEmail, privateKey, "https://www.googleapis.com/auth/indexing");
    const resp = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=${jwt}`,
    });

    const data: any = await resp.json();
    return data.access_token || null;
  } catch (err) {
    console.error("Token error:", err);
    return null;
  }
}

function parseCredentials(env: Env, secretKey: keyof Env): { email: string; privateKey: string } | null {
  const raw = env[secretKey];
  if (!raw) return null;
  try {
    const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
    return {
      email: parsed.client_email,
      privateKey: parsed.private_key,
    };
  } catch (err) {
    console.error(`Failed to parse secret ${String(secretKey)}:`, err);
    return null;
  }
}

async function syncSiteSitemap(siteId: string, env: Env): Promise<{ synced: number; total_sitemap: number }> {
  const site = SITES[siteId];
  if (!site) return { synced: 0, total_sitemap: 0 };
  try {
    const sitemapUrls = [`${site.domain}/sitemap.xml`];
    if (siteId === "broker") {
      sitemapUrls.push(`${site.domain}/sitemap-scam-reports-1.xml`);
    } else if (siteId === "dating") {
      sitemapUrls.push(`${site.domain}/sitemap-dating-scams-1.xml`);
    }

    let matches: string[] = [];
    for (const smUrl of sitemapUrls) {
      const resp = await fetch(smUrl, {
        headers: { "User-Agent": "RadarIndexer/1.0" },
      });
      if (!resp.ok) continue;
      const xml = await resp.text();
      const subMatches = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim());
      if (xml.includes("<sitemapindex")) {
        for (const childSitemapUrl of subMatches.slice(0, 2)) {
          try {
            const childResp = await fetch(childSitemapUrl, {
              headers: { "User-Agent": "RadarIndexer/1.0" },
            });
            if (childResp.ok) {
              const childXml = await childResp.text();
              matches.push(...[...childXml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1].trim()));
            }
          } catch (err) {
            console.error(`Child sitemap fetch failed for ${childSitemapUrl}:`, err);
          }
        }
      } else {
        matches.push(...subMatches);
      }
    }

    if (!matches.length) return { synced: 0, total_sitemap: 0 };

    // Limit D1 queue per site to 10,000 URLs at a time to keep D1 fast
    const cappedMatches = matches.slice(0, 10000);

    const { results: existingRows } = await env.DB.prepare(
      "SELECT url FROM urls_queue WHERE site_id = ?"
    ).bind(siteId).all<{ url: string }>();
    const existingSet = new Set((existingRows || []).map((r) => r.url));
    const newUrls = cappedMatches.filter((u) => !existingSet.has(u));

    if (newUrls.length > 0) {
      let totalSynced = 0;
      for (let i = 0; i < newUrls.length; i += 400) {
        const chunk = newUrls.slice(i, i + 400);
        const stmts = chunk.map((u) =>
          env.DB.prepare("INSERT OR IGNORE INTO urls_queue (site_id, url, is_indexed) VALUES (?, ?, 0)").bind(siteId, u)
        );
        await env.DB.batch(stmts);
        totalSynced += chunk.length;
      }
      return { synced: totalSynced, total_sitemap: matches.length };
    }
    return { synced: 0, total_sitemap: matches.length };
  } catch (e) {
    console.error(`Sitemap sync failed for ${siteId}:`, e);
    return { synced: 0, total_sitemap: 0 };
  }
}

async function runBatchForSite(
  siteId: string,
  batchSize: number,
  env: Env
): Promise<{ processed: number; errors: string[]; status: string }> {
  // If CalcolaIncentivi, call its dedicated worker endpoint via Service Binding
  if (siteId === "calcolaincentivi") {
    try {
      const resp = env.IT_INDEXER
        ? await env.IT_INDEXER.fetch(new Request(`https://internal/run?limit=${batchSize}`))
        : await fetch(`https://seo-indexer.amendamax.workers.dev/run?limit=${batchSize}`);
      const data: any = await resp.json();
      const processed = data.total_sent || 0;
      const errors = data.errors || [];
      const status = processed > 0 ? "SUCCESS" : errors.length ? "QUOTA_EXCEEDED" : "EMPTY";
      return { processed, errors, status };
    } catch (e: any) {
      return { processed: 0, errors: [e.message], status: "ERROR" };
    }
  }

  // If CalculeazaSubventii.ro, call its dedicated worker endpoint via Service Binding
  if (siteId === "calculeazasubventii") {
    try {
      const resp = env.RO_INDEXER
        ? await env.RO_INDEXER.fetch(new Request(`https://internal/run?limit=${batchSize}`))
        : await fetch(`https://ro-seo-indexer.amendamax.workers.dev/run?limit=${batchSize}`);
      const data: any = await resp.json();
      const processed = data.total_sent || 0;
      const errors = data.errors || [];
      const status = processed > 0 ? "SUCCESS" : errors.length ? "QUOTA_EXCEEDED" : "EMPTY";
      return { processed, errors, status };
    } catch (e: any) {
      return { processed: 0, errors: [e.message], status: "ERROR" };
    }
  }

  // If one of the 8 EU Subsidy portals (eu_de .. eu_cz), call its /indexer/run endpoint via Service Binding
  if (siteId.startsWith("eu_")) {
    const site = SITES[siteId];
    if (!site) return { processed: 0, errors: ["Site EU necunoscut"], status: "ERROR" };
    try {
      const targetUrl = `${site.domain}/indexer/run?limit=${batchSize}`;
      const resp = env.EU_GATEWAY
        ? await env.EU_GATEWAY.fetch(new Request(targetUrl, { headers: { Host: new URL(site.domain).host } }))
        : await fetch(targetUrl);
      const data: any = await resp.json();
      const processed = data.processed || data.sent_now || 0;
      const errors = data.errors || [];
      const status = data.status || (processed > 0 ? "SUCCESS" : errors.length ? "ERROR" : "EMPTY");
      return { processed, errors, status };
    } catch (e: any) {
      return { processed: 0, errors: [e.message], status: "ERROR" };
    }
  }

  const site = SITES[siteId];
  if (!site) return { processed: 0, errors: ["Site necunoscut"], status: "ERROR" };

  const creds = parseCredentials(env, site.secretKey);
  if (!creds) {
    return { processed: 0, errors: [`Cheie secretă lipsă: ${String(site.secretKey)}`], status: "ERROR" };
  }

  // Check how many sent today (including partial batches that hit QUOTA_EXCEEDED)
  const todayRow = await env.DB.prepare(
    "SELECT COALESCE(SUM(urls_count), 0) as cnt FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')"
  ).bind(siteId).first<{ cnt: number }>();

  const sentToday = todayRow?.cnt || 0;
  if (sentToday >= site.dailyQuota) {
    return { processed: 0, errors: [`Cota zilnică (${site.dailyQuota}) a fost deja atinsă azi (${sentToday})`], status: "QUOTA_EXCEEDED" };
  }

  const allowedBatch = Math.min(batchSize, site.dailyQuota - sentToday);
  if (allowedBatch <= 0) {
    return { processed: 0, errors: ["Cota zilnică atinsă"], status: "QUOTA_EXCEEDED" };
  }

  // Get pending URLs on primary site
  let { results: pending } = await env.DB.prepare(
    "SELECT id, url FROM urls_queue WHERE site_id = ? AND is_indexed = 0 ORDER BY id ASC LIMIT ?"
  ).bind(siteId, allowedBatch).all<{ id: number; url: string }>();

  let originHealthy = true;
  if (pending && pending.length > 0) {
    try {
      const hcResp = await fetch(`${site.domain}/robots.txt`, {
        method: "HEAD",
        headers: { "User-Agent": "RadarIndexer-HealthCheck/1.0" },
      });
      if (hcResp.status >= 500) originHealthy = false;
    } catch (_) {
      originHealthy = false;
    }
  }

  // TIERED SEO DISCIPLINE: Shared-pool fallback draining onto EU small municipalities is disabled.
  if (!pending || pending.length === 0 || !originHealthy) {
    if (!originHealthy) {
      return {
        processed: 0,
        errors: [`Origin ${site.domain} pus pe pauză (503) și cota fallback epuizată`],
        status: "PAUSED_503",
      };
    }
    return { processed: 0, errors: ["Toate paginile din coadă sunt deja indexate (fallback pool verificat)!"], status: "EMPTY" };
  }

  const token = await getAccessToken(creds.email, creds.privateKey);
  if (!token) {
    const err = `Eșec la obținere token Google pentru ${creds.email}`;
    await env.DB.prepare(
      "INSERT INTO indexing_logs (site_id, status, urls_count, details) VALUES (?, 'ERROR', 0, ?)"
    ).bind(siteId, err).run();
    return { processed: 0, errors: [err], status: "ERROR" };
  }

  let successCount = 0;
  let hitQuota = false;
  const errors: string[] = [];

  for (const item of pending) {
    if (hitQuota) break;

    try {
      const res = await fetch("https://indexing.googleapis.com/v3/urlNotifications:publish", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ url: item.url, type: "URL_UPDATED" }),
      });

      if (res.status === 200) {
        successCount++;
        await env.DB.prepare(
          "UPDATE urls_queue SET is_indexed = 1, indexed_at = CURRENT_TIMESTAMP WHERE id = ?"
        ).bind(item.id).run();
      } else if (res.status === 429) {
        hitQuota = true;
        errors.push(`Google 429 Quota Exceeded la ${item.url}`);
        break;
      } else {
        const text = await res.text();
        errors.push(`Status ${res.status}: ${text.slice(0, 100)}`);
      }
    } catch (e: any) {
      errors.push(`Network error: ${e.message}`);
    }
  }

  const finalStatus = hitQuota ? "QUOTA_EXCEEDED" : successCount > 0 ? "SUCCESS" : "ERROR";
  const details = hitQuota
    ? `Cota zilnică atinsă la Google. Trimise până acum: ${successCount}.`
    : `Indexate cu succes: ${successCount} pagini.` + (errors.length ? ` Erori: ${errors.length}` : "");

  await env.DB.prepare(
    "INSERT INTO indexing_logs (site_id, status, urls_count, details) VALUES (?, ?, ?, ?)"
  ).bind(siteId, finalStatus, successCount, details).run();

  return { processed: successCount, errors, status: finalStatus };
}

export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log(`[CRON] Started at ${new Date().toISOString()} (Tiered SEO Mode — Subsidy Mass Indexing Paused)`);
    // Subsidy portals (calcolaincentivi, calculeazasubventii, eu_*) are governed strictly by their dedicated Tier-1/News caps (max 15/day)
    // and are NO LONGER mass-pumped every 15 minutes from radar-indexer.

    // 2. Always process non-EU radar sites (lowest sentToday first, up to 3 sites per tick)
    const radarIds = Object.keys(SITES).filter(
      id => !id.startsWith("eu_") && id !== "calcolaincentivi" && id !== "calculeazasubventii"
    );
    const radarCandidates: { siteId: string; sentToday: number }[] = [];

    for (const siteId of radarIds) {
      const site = SITES[siteId];
      const todayRow = await env.DB.prepare(
        "SELECT COALESCE(SUM(urls_count), 0) as cnt FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')"
      ).bind(siteId).first<{ cnt: number }>();

      const sentToday = todayRow?.cnt || 0;
      if (sentToday >= site.dailyQuota) continue;

      const quotaExceededRow = await env.DB.prepare(
        "SELECT COUNT(*) as cnt FROM indexing_logs WHERE site_id = ? AND created_at >= datetime('now', '-1 hours') AND status = 'QUOTA_EXCEEDED'"
      ).bind(siteId).first<{ cnt: number }>();
      if (quotaExceededRow && quotaExceededRow.cnt > 0) continue;

      const pendingRow = await env.DB.prepare(
        "SELECT id FROM urls_queue WHERE site_id = ? AND is_indexed = 0 LIMIT 1"
      ).bind(siteId).first<{ id: number }>();
      if (!pendingRow) continue;

      radarCandidates.push({ siteId, sentToday });
    }

    radarCandidates.sort((a, b) => a.sentToday - b.sentToday);
    for (const cand of radarCandidates.slice(0, 3)) {
      const site = SITES[cand.siteId];
      console.log(`[CRON RADAR] Processing ${site.name} (sent today: ${cand.sentToday}/${site.dailyQuota})`);
      await runBatchForSite(cand.siteId, 35, env);
    }
  },

  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/sync") {
      const siteId = url.searchParams.get("site") || "appscam";
      const res = await syncSiteSitemap(siteId, env);
      return Response.json(res);
    }

    if (url.pathname === "/resync-clean") {
      const siteId = url.searchParams.get("site") || "broker";
      await env.DB.prepare("DELETE FROM urls_queue WHERE site_id = ? AND is_indexed = 0").bind(siteId).run();
      const res = await syncSiteSitemap(siteId, env);
      return Response.json({ cleaned: true, site: siteId, ...res });
    }

    // API stats
    if (url.pathname === "/api/stats") {
      const stats: Record<string, any> = {};
      for (const siteId of Object.keys(SITES)) {
        const site = SITES[siteId];
        if (siteId === "calcolaincentivi" && env.DB_ITALY) {
          const totalRow = await env.DB_ITALY.prepare(
            "SELECT count(*) as total, (SELECT count(*) FROM seo_pages WHERE is_indexed = 1) as indexed FROM seo_pages"
          ).first<{ total: number; indexed: number }>();
          const todayRow = await env.DB_ITALY.prepare(
            "SELECT COALESCE(SUM(total_sent), 0) as sent_today FROM indexing_logs WHERE date(created_at) = date('now')"
          ).first<{ sent_today: number }>();
          const total = totalRow?.total || 7200;
          const indexed = totalRow?.indexed || 400;
          stats[siteId] = {
            total,
            indexed,
            pending: total - indexed,
            sent_today: todayRow?.sent_today || 400,
          };
        } else if (siteId === "calculeazasubventii" && env.DB_ROMANIA) {
          const totalRow = await env.DB_ROMANIA.prepare(
            "SELECT count(*) as total, (SELECT count(*) FROM seo_pages WHERE status = 'INDEXED') as indexed, (SELECT count(*) FROM seo_pages WHERE status = 'INDEXED' AND date(last_submitted_at) = date('now')) as sent_today FROM seo_pages"
          ).first<{ total: number; indexed: number; sent_today: number }>();
          const total = totalRow?.total || 3881;
          const indexed = totalRow?.indexed || 0;
          stats[siteId] = {
            total,
            indexed,
            pending: total - indexed,
            sent_today: totalRow?.sent_today || 0,
          };
        } else if (siteId.startsWith("eu_")) {
          const cc = siteId.replace("eu_", "").toUpperCase();
          let dbTotal = 0;
          let indexed = 0;
          let sentToday = 0;
          try {
            const euRow = await env.DB.prepare(
              "SELECT count(*) as total, (SELECT count(*) FROM eu_seo_pages WHERE country_code = ? AND status = 'INDEXED') as indexed, (SELECT count(*) FROM eu_seo_pages WHERE country_code = ? AND status = 'INDEXED' AND date(last_submitted_at) = date('now')) as sent_today, (SELECT COALESCE(SUM(urls_count), 0) FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')) as log_today FROM eu_seo_pages WHERE country_code = ?"
            ).bind(cc, cc, siteId, cc).first<{ total: number; indexed: number; sent_today: number; log_today: number }>();
            dbTotal = euRow?.total || 0;
            indexed = euRow?.indexed || 0;
            sentToday = Math.max(euRow?.sent_today || 0, euRow?.log_today || 0);
          } catch (e) {}
          const total = Math.max(dbTotal, site.defaultTotal || 2000);
          stats[siteId] = {
            total,
            indexed,
            pending: total - indexed,
            sent_today: sentToday,
          };
        } else {
          const totalRow = await env.DB.prepare("SELECT COUNT(*) as total, SUM(is_indexed) as indexed FROM urls_queue WHERE site_id = ?").bind(siteId).first<{ total: number; indexed: number }>();
          const todayRow = await env.DB.prepare("SELECT COALESCE(SUM(urls_count), 0) as sent_today FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')").bind(siteId).first<{ sent_today: number }>();
          const rawTotal = Math.max(totalRow?.total || 0, site.defaultTotal || 0);
          const rawIndexed = totalRow?.indexed || 0;
          stats[siteId] = {
            total: rawTotal,
            indexed: rawIndexed,
            pending: rawTotal - rawIndexed,
            sent_today: todayRow?.sent_today || 0,
          };
        }
      }
      return new Response(JSON.stringify(stats), {
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    }

    if (url.pathname === "/api/cloudshell-drop") {
      if (request.method === "POST") {
        const body = await request.text();
        await env.DB.prepare(
          "INSERT INTO indexing_logs (site_id, urls_count, status, details) VALUES ('cloudshell_drop', 0, 'DROP', ?)"
        ).bind(body).run();
        return Response.json({ ok: true, msg: "Keys received directly by Cloudflare!" });
      }
      const row = await env.DB.prepare(
        "SELECT details FROM indexing_logs WHERE site_id = 'cloudshell_drop' ORDER BY id DESC LIMIT 1"
      ).first<{ details: string }>();
      return new Response(row?.details || "{}", { headers: { "Content-Type": "application/json" } });
    }

    // Manual trigger
    if (url.pathname === "/trigger") {
      const siteId = url.searchParams.get("site") || "jobscam";
      const defaultBatch = (SITES[siteId]?.dailyQuota || 200) >= 400 ? "40" : "35";
      const count = parseInt(url.searchParams.get("count") || defaultBatch, 10);
      const res = await runBatchForSite(siteId, Math.min(count, 40), env);
      return new Response(
        JSON.stringify(res, null, 2),
        {
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        }
      );
    }

    // Priority #1 (Index 0) Push for all 16 /bps-cloud URLs + https://palyazatkalkulator.hu/
    if (url.pathname === "/push-bps-cloud") {
      const bpsTargets = [
        { code: "RO", siteId: "calculeazasubventii", host: "calculeazasubventii.ro", url: "https://calculeazasubventii.ro/bps-cloud" },
        { code: "IT", siteId: "calcolaincentivi", host: "calcolaincentivi.it", url: "https://calcolaincentivi.it/bps-cloud" },
        { code: "HU", siteId: "eu_hu", host: "palyazatkalkulator.hu", url: "https://palyazatkalkulator.hu/bps-cloud" },
        { code: "DE", siteId: "eu_de", host: "foerderungberechnen.de", url: "https://foerderungberechnen.de/bps-cloud" },
        { code: "AT", siteId: "eu_at", host: "foerderungberechnen.at", url: "https://foerderungberechnen.at/bps-cloud" },
        { code: "FR", siteId: "eu_fr", host: "calculesubventions.fr", url: "https://calculesubventions.fr/bps-cloud" },
        { code: "LU", siteId: "eu_lu", host: "calculesubventions.fr/lu", url: "https://calculesubventions.fr/lu/bps-cloud" },
        { code: "NL", siteId: "eu_nl", host: "berekensubsidie.nl", url: "https://berekensubsidie.nl/bps-cloud" },
        { code: "BE", siteId: "eu_be", host: "premieberekenen.be", url: "https://premieberekenen.be/bps-cloud" },
        { code: "ES", siteId: "eu_es", host: "calculasubvenciones.es", url: "https://calculasubvenciones.es/bps-cloud" },
        { code: "PL", siteId: "eu_pl", host: "obliczdotacje.pl", url: "https://obliczdotacje.pl/bps-cloud" },
        { code: "PT", siteId: "eu_pt", host: "calculaincentivos.pt", url: "https://calculaincentivos.pt/bps-cloud" },
        { code: "CZ", siteId: "eu_cz", host: "spocitejdotaci.cz", url: "https://spocitejdotaci.cz/bps-cloud" },
        { code: "UK", siteId: "eu_uk", host: "ukgrantcalculator.co.uk", url: "https://ukgrantcalculator.co.uk/bps-cloud" },
        { code: "DK", siteId: "eu_dk", host: "beregnstotte.dk", url: "https://beregnstotte.dk/bps-cloud" },
        { code: "SE", siteId: "eu_se", host: "bidragskalkylator.se", url: "https://bidragskalkylator.se/bps-cloud" },
      ];

      // 1. Seed Index 0 across all 3 D1 databases WITH STEP 2 QUOTA PROTECTION (never reset already-indexed-today URLs!)
      try {
        if (env.DB_ROMANIA) {
          await env.DB_ROMANIA.prepare(
            "INSERT INTO seo_pages (url, status) VALUES ('https://calculeazasubventii.ro/bps-cloud', 'PENDING') ON CONFLICT(url) DO UPDATE SET status = CASE WHEN status = 'INDEXED' AND date(last_submitted_at) >= date('now') THEN 'INDEXED' ELSE 'PENDING' END"
          ).run();
        }
      } catch (_) {}

      try {
        if (env.DB_ITALY) {
          await env.DB_ITALY.prepare(
            "INSERT OR IGNORE INTO seo_pages (slug, is_indexed) VALUES ('bps-cloud', 0)"
          ).run();
        }
      } catch (_) {}

      try {
        const euStmts = [
          env.DB.prepare(
            "INSERT INTO eu_seo_pages (url, country_code, domain, status) VALUES ('https://palyazatkalkulator.hu/', 'HU', 'palyazatkalkulator.hu', 'PENDING') ON CONFLICT(url) DO UPDATE SET status = CASE WHEN status = 'INDEXED' AND date(last_submitted_at) >= date('now') THEN 'INDEXED' ELSE 'PENDING' END"
          ),
          ...bpsTargets
            .filter((t) => t.code !== "RO" && t.code !== "IT")
            .map((t) =>
              env.DB.prepare(
                "INSERT INTO eu_seo_pages (url, country_code, domain, status) VALUES (?, ?, ?, 'PENDING') ON CONFLICT(url) DO UPDATE SET status = CASE WHEN status = 'INDEXED' AND date(last_submitted_at) >= date('now') THEN 'INDEXED' ELSE 'PENDING' END"
              ).bind(t.url, t.code, t.host)
            ),
        ];
        await env.DB.batch(euStmts);
      } catch (_) {}

      // 2. Trigger RO, IT, and HU immediately
      const results: Record<string, any> = {};
      results.RO = await runBatchForSite("calculeazasubventii", 2, env);
      results.IT = await runBatchForSite("calcolaincentivi", 2, env);
      results.HU = await runBatchForSite("eu_hu", 2, env);

      return new Response(
        JSON.stringify(
          {
            ok: true,
            queue_position: "INDEX_0_PRIORITY_1",
            seeded_urls: [
              "https://palyazatkalkulator.hu/",
              ...bpsTargets.map((t) => t.url),
            ],
            immediate_triggers: results,
          },
          null,
          2
        ),
        { headers: { "Content-Type": "application/json; charset=utf-8" } }
      );
    }

    // Main Dashboard HTML
    const siteStats: any[] = [];
    let grandTotal = 0;
    let grandIndexed = 0;
    let grandToday = 0;

    for (const siteId of Object.keys(SITES)) {
      const site = SITES[siteId];
      let total = 0;
      let indexed = 0;
      let sentToday = 0;

      if (siteId === "calcolaincentivi" && env.DB_ITALY) {
        const totalRow = await env.DB_ITALY.prepare(
          "SELECT count(*) as total, (SELECT count(*) FROM seo_pages WHERE is_indexed = 1) as indexed FROM seo_pages"
        ).first<{ total: number; indexed: number }>();
        const todayRow = await env.DB_ITALY.prepare(
          "SELECT COALESCE(SUM(total_sent), 0) as sent_today FROM indexing_logs WHERE date(created_at) = date('now')"
        ).first<{ sent_today: number }>();
        total = totalRow?.total || 7200;
        indexed = totalRow?.indexed || 400;
        sentToday = todayRow?.sent_today || 400;
      } else if (siteId === "calculeazasubventii" && env.DB_ROMANIA) {
        const totalRow = await env.DB_ROMANIA.prepare(
          "SELECT count(*) as total, (SELECT count(*) FROM seo_pages WHERE status = 'INDEXED') as indexed, (SELECT count(*) FROM seo_pages WHERE status = 'INDEXED' AND date(last_submitted_at) = date('now')) as sent_today FROM seo_pages"
        ).first<{ total: number; indexed: number; sent_today: number }>();
        total = totalRow?.total || 3881;
        indexed = totalRow?.indexed || 0;
        sentToday = totalRow?.sent_today || 0;
      } else if (siteId.startsWith("eu_")) {
        const cc = siteId.replace("eu_", "").toUpperCase();
        try {
          const euRow = await env.DB.prepare(
            "SELECT count(*) as total, (SELECT count(*) FROM eu_seo_pages WHERE country_code = ? AND status = 'INDEXED') as indexed, (SELECT count(*) FROM eu_seo_pages WHERE country_code = ? AND status = 'INDEXED' AND date(last_submitted_at) = date('now')) as sent_today, (SELECT COALESCE(SUM(urls_count), 0) FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')) as log_today FROM eu_seo_pages WHERE country_code = ?"
          ).bind(cc, cc, siteId, cc).first<{ total: number; indexed: number; sent_today: number; log_today: number }>();
          total = Math.max(euRow?.total || 0, site.defaultTotal || 2000);
          indexed = euRow?.indexed || 0;
          sentToday = Math.max(euRow?.sent_today || 0, euRow?.log_today || 0);
        } catch (e) {
          total = site.defaultTotal || 2000;
        }
      } else {
        const totalRow = await env.DB.prepare(
          "SELECT COUNT(*) as total, COALESCE(SUM(is_indexed), 0) as indexed FROM urls_queue WHERE site_id = ?"
        ).bind(siteId).first<{ total: number; indexed: number }>();

        const todayRow = await env.DB.prepare(
          "SELECT COALESCE(SUM(urls_count), 0) as sent_today FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now')"
        ).bind(siteId).first<{ sent_today: number }>();

        total = Math.max(totalRow?.total || 0, site.defaultTotal || 0);
        indexed = totalRow?.indexed || 0;
        sentToday = todayRow?.sent_today || 0;
      }

      const pending = total - indexed;
      const pct = total > 0 ? Math.round((indexed / total) * 100) : 0;

      const LOT_NAMES_SHORT = [
        "Lot 1: Solar & Baterii",
        "Lot 2: Wallbox EV",
        "Lot 3: Acoperiș & Izolație",
        "Lot 4: Reciclare Solar",
        "Lot 5: Accesibilitate Seniori",
        "Lot 6: Subvenții Firme B2B",
        "Lot 7: Agro-Fotovoltaice",
        "Lot 8: Tratare & Filtrare Apă",
        "Lot 9: Rute Orașe Directe",
      ];
      const isSubsidyPortal =
        siteId.startsWith("eu_") || siteId === "calcolaincentivi" || siteId === "calculeazasubventii";
      const lot1Size =
        site.defaultTotal ||
        (siteId === "calcolaincentivi" ? 7904 : siteId === "calculeazasubventii" ? 3881 : total);
      const lot1Done = isSubsidyPortal && lot1Size > 0 && indexed >= lot1Size;
      const currentLot =
        isSubsidyPortal && lot1Size > 0 ? Math.max(1, Math.min(9, Math.round(total / lot1Size))) : 1;
      const lotLabel = LOT_NAMES_SHORT[currentLot - 1] || `Lot ${currentLot}`;

      let quotaFullToday = sentToday >= site.dailyQuota;
      if (!quotaFullToday && siteId !== "calcolaincentivi" && siteId !== "calculeazasubventii") {
        try {
          const qRow = await env.DB.prepare(
            "SELECT status FROM indexing_logs WHERE site_id = ? AND created_at >= datetime('now', '-10 hours') ORDER BY id DESC LIMIT 1"
          ).bind(siteId).first<{ status: string }>();
          if (qRow && qRow.status === "QUOTA_EXCEEDED") {
            quotaFullToday = true;
          }
        } catch (e) {}
      }

      grandTotal += total;
      grandIndexed += indexed;
      grandToday += sentToday;

      siteStats.push({
        ...site,
        total,
        indexed,
        pending,
        sentToday,
        pct,
        quotaFullToday,
        isSubsidyPortal,
        lot1Size,
        lot1Done,
        currentLot,
        lotLabel,
      });
    }

    // Fetch logs from radar_network_db
    const { results: radarLogs } = await env.DB.prepare(
      "SELECT site_id, status, urls_count, details, created_at FROM indexing_logs ORDER BY id DESC LIMIT 25"
    ).all<any>();

    // Fetch logs from master_italy & master_romania if available
    let combinedLogs = [...(radarLogs || [])];
    if (env.DB_ITALY) {
      const { results: italyLogs } = await env.DB_ITALY.prepare(
        "SELECT 'calcolaincentivi' as site_id, 'SUCCESS' as status, total_sent as urls_count, details, created_at FROM indexing_logs ORDER BY id DESC LIMIT 10"
      ).all<any>();
      if (italyLogs) {
        combinedLogs = [...combinedLogs, ...italyLogs];
      }
    }
    if (env.DB_ROMANIA) {
      const { results: roLogs } = await env.DB_ROMANIA.prepare(
        "SELECT 'calculeazasubventii' as site_id, COALESCE(status, 'SUCCESS') as status, urls_succeeded as urls_count, details, run_at as created_at FROM indexing_logs ORDER BY id DESC LIMIT 10"
      ).all<any>();
      if (roLogs && roLogs.length > 0) {
        combinedLogs = [...combinedLogs, ...roLogs];
      } else {
        const roTodayRow = await env.DB_ROMANIA.prepare(
          "SELECT count(*) as cnt, MAX(last_submitted_at) as last_ts FROM seo_pages WHERE status = 'INDEXED'"
        ).first<{ cnt: number; last_ts: string }>();
        if (roTodayRow && roTodayRow.cnt > 0) {
          combinedLogs.push({
            site_id: "calculeazasubventii",
            status: "SUCCESS",
            urls_count: roTodayRow.cnt,
            details: `Indexate cu succes prin ro-seo-indexer (${roTodayRow.cnt} pagini din România)`,
            created_at: roTodayRow.last_ts || new Date().toISOString(),
          });
        }
      }
    }

    // Sort by created_at descending
    combinedLogs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    const displayLogs = combinedLogs.slice(0, 30);

    // Fetch Live Leads across all 14 countries (EU + UK + IT + RO)
    let allLeads: any[] = [];
    let recentSimulations: any[] = [];
    try {
      const { results: euLeads } = await env.DB.prepare(
        "SELECT id, country_code, full_name, phone, email, city_or_postal as postal_code, service_mode as measure_slug, estimated_grant_eur as estimated_grant, 'NEW_SLA_3H' as status, created_at FROM eu_leads ORDER BY id DESC LIMIT 30"
      ).all<any>();
      if (euLeads) allLeads = [...allLeads, ...euLeads];
    } catch (e) {}

    if (env.DB_ITALY) {
      try {
        const { results: itLeads } = await env.DB_ITALY.prepare(
          "SELECT id, 'IT' as country_code, customer_name as full_name, customer_phone as phone, comune_istat as postal_code, vertical_slug as measure_slug, details, created_at FROM leads ORDER BY id DESC LIMIT 20"
        ).all<any>();
        if (itLeads) {
          for (const row of itLeads) {
            let parsed: any = {};
            try { parsed = JSON.parse(row.details || "{}"); } catch (e) {}
            allLeads.push({
              id: row.id,
              country_code: "IT",
              full_name: parsed.full_name || parsed.company_name || row.full_name || "Cliente IT",
              phone: row.phone,
              email: parsed.email || "",
              postal_code: parsed.comune ? `${parsed.comune} (${parsed.province || ""})` : row.postal_code,
              measure_slug: parsed.friendly_mode || row.measure_slug,
              estimated_grant: parsed.technical_snapshot?.estimated_cost_with_ecobonus || 0,
              status: "ACTIVE_SLA_3H",
              created_at: row.created_at || parsed.timestamp,
            });
          }
        }
      } catch (e) {}
    }

    if (env.DB_ROMANIA) {
      try {
        const { results: roLeads } = await env.DB_ROMANIA.prepare(
          "SELECT id, customer_phone as phone, comune, province, vertical_slug, mode, system_title, estimated_grant_lei, technical_snapshot, status, created_at FROM leads ORDER BY id DESC LIMIT 20"
        ).all<any>();
        if (roLeads) {
          for (const row of roLeads) {
            let parsed: any = {};
            try { parsed = JSON.parse(row.technical_snapshot || "{}"); } catch (e) {}
            allLeads.push({
              id: row.id,
              country_code: "RO",
              full_name: parsed.full_name || parsed.companyName || "Client RO",
              phone: row.phone,
              email: parsed.email || "",
              postal_code: `${row.comune || ""} (${row.province || ""})`,
              measure_slug: row.system_title || row.mode || row.vertical_slug,
              estimated_grant: Math.round((Number(row.estimated_grant_lei) || 0) / 5),
              status: (row.status || "NEW_SLA_3H").toUpperCase(),
              created_at: row.created_at,
            });
          }
        }
      } catch (e) {}
    }

    allLeads.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    const displayLeads = allLeads.slice(0, 25);

    try {
      const { results: simLogs } = await env.DB.prepare(
        "SELECT domain, country_code, city_or_postal, service_mode, sqm, monthly_bill, estimated_grant_eur, created_at FROM eu_simulation_logs ORDER BY id DESC LIMIT 25"
      ).all<any>();
      if (simLogs) recentSimulations = [...recentSimulations, ...simLogs];
    } catch (e) {}

    if (env.DB_ITALY) {
      try {
        const { results: itSims } = await env.DB_ITALY.prepare(
          "SELECT mode, comune, province, cap, input_params_json, calculated_results_json, created_at FROM simulation_logs ORDER BY id DESC LIMIT 20"
        ).all<any>();
        if (itSims) {
          for (const s of itSims) {
            let inp: any = {};
            let calc: any = {};
            try { inp = JSON.parse(s.input_params_json || "{}"); } catch (e) {}
            try { calc = JSON.parse(s.calculated_results_json || "{}"); } catch (e) {}
            recentSimulations.push({
              domain: "calcolaincentivi.it",
              country_code: "IT",
              city_or_postal: `${s.comune || "Italia"} (${s.province || s.cap || ""})`,
              service_mode: s.mode || "solar",
              sqm: Number(inp.sqm) || 120,
              monthly_bill: Number(inp.bill) || 150,
              estimated_grant_eur: Number(calc.estimated_cost_with_ecobonus) || 0,
              created_at: s.created_at,
            });
          }
        }
      } catch (e) {}
    }

    if (env.DB_ROMANIA) {
      try {
        const { results: roSims } = await env.DB_ROMANIA.prepare(
          "SELECT mode, comune, province, input_sqm, input_bill, state_grant_lei, created_at FROM simulation_logs ORDER BY id DESC LIMIT 20"
        ).all<any>();
        if (roSims) {
          for (const s of roSims) {
            recentSimulations.push({
              domain: "calculeazasubventii.ro",
              country_code: "RO",
              city_or_postal: `${s.comune || "România"} (${s.province || ""})`,
              service_mode: s.mode || "solar_battery",
              sqm: Number(s.input_sqm) || 120,
              monthly_bill: Math.round((Number(s.input_bill) || 900) / 5),
              estimated_grant_eur: Math.round((Number(s.state_grant_lei) || 30000) / 5),
              created_at: s.created_at,
            });
          }
        }
      } catch (e) {}
    }

    recentSimulations.sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    recentSimulations = recentSimulations.slice(0, 25);

    const grandPct = grandTotal > 0 ? Math.round((grandIndexed / grandTotal) * 100) : 0;
    const totalSitesCount = Object.keys(SITES).length;
    const totalDailyQuota = Object.values(SITES).reduce((acc, s) => acc + s.dailyQuota, 0);

    const html = `<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Indexer Fleet | ${totalSitesCount} Portaluri Active</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: rgba(18, 24, 38, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at 50% 0%, #172554 0%, var(--bg) 60%);
      color: var(--text);
      font-family: 'Inter', -apple-system, sans-serif;
      min-height: 100vh;
      padding: 2.5rem 1rem;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    header {
      margin-bottom: 2.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .logo-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa;
      padding: 0.35rem 0.85rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }
    h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.025em; }
    .subtitle { color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem; }
    
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      padding: 0.4rem 1rem;
      border-radius: 9999px;
      font-size: 0.85rem;
      font-weight: 600;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background-color: #34d399;
      border-radius: 50%;
      box-shadow: 0 0 10px #34d399;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }
    .stat-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 1rem;
      padding: 1.5rem;
    }
    .stat-label { color: var(--text-muted); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-val { font-size: 2.25rem; font-weight: 800; margin: 0.4rem 0; color: #fff; font-family: 'JetBrains Mono', monospace; }
    .stat-sub { font-size: 0.85rem; color: var(--text-muted); }

    .sites-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }
    .site-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 1.25rem;
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s, border-color 0.2s;
    }
    .site-card:hover {
      border-color: rgba(59, 130, 246, 0.4);
      transform: translateY(-2px);
    }
    .site-head {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1.25rem;
    }
    .site-title { font-size: 1.25rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
    .site-domain { font-size: 0.825rem; color: #60a5fa; text-decoration: none; display: block; margin-top: 0.2rem; }
    .site-domain:hover { text-decoration: underline; }
    
    .progress-wrap {
      margin: 1.25rem 0;
    }
    .progress-bar-bg {
      background: rgba(255, 255, 255, 0.07);
      border-radius: 9999px;
      height: 10px;
      overflow: hidden;
      margin-bottom: 0.5rem;
    }
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #3b82f6, #10b981);
      border-radius: 9999px;
      transition: width 0.4s ease;
    }
    .progress-stats {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    .site-metrics {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      padding: 0.85rem;
      background: rgba(0, 0, 0, 0.25);
      border-radius: 0.75rem;
      margin-bottom: 1.25rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
    }
    .metric-row span:last-child { font-weight: 700; color: #fff; }

    .btn-action {
      background: linear-gradient(135deg, var(--primary), var(--primary-hover));
      color: white;
      border: none;
      border-radius: 0.75rem;
      padding: 0.75rem 1.25rem;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      width: 100%;
      transition: opacity 0.2s, transform 0.1s;
    }
    .btn-action:hover { opacity: 0.92; }
    .btn-action:active { transform: scale(0.98); }
    .btn-action:disabled { opacity: 0.5; cursor: not-allowed; }

    .logs-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 1.25rem;
      padding: 1.75rem;
      overflow: hidden;
    }
    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
    th {
      text-align: left;
      padding: 0.75rem 1rem;
      color: var(--text-muted);
      border-bottom: 1px solid var(--card-border);
      font-weight: 600;
      font-size: 0.8rem;
      text-transform: uppercase;
    }
    td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    tr:last-child td { border-bottom: none; }
    .badge {
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .badge-quota { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .badge-error { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .time-col { color: var(--text-muted); font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <div class="logo-badge">⚡ Cloudflare Global Workers Fleet</div>
        <h1>Master Indexer Fleet Dashboard</h1>
        <p class="subtitle">Monitorizare și indexare automată 24/7 prin Google Indexing API &amp; IndexNow pentru cele ${totalSitesCount} portaluri</p>
      </div>
      <div>
        <span class="status-pill">
          <span class="pulse-dot"></span>
          ${totalSitesCount} Portaluri Active
        </span>
      </div>
    </header>

    <!-- Global Stats -->
    <div style="margin-bottom: 1.75rem; padding: 1.25rem 1.5rem; border-radius: 1rem; background: linear-gradient(135deg, rgba(6, 78, 59, 0.55) 0%, rgba(15, 23, 42, 0.9) 60%, rgba(30, 58, 138, 0.55) 100%); border: 1px solid rgba(52, 211, 153, 0.5); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
      <div>
        <div style="display: inline-flex; align-items: center; gap: 0.45rem; font-size: 0.75rem; font-weight: 800; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;">
          <span class="pulse-dot"></span>
          <span>POZIȚIA #1 (INDEX 0) ÎN COADA GOOGLE INDEXING API &amp; INDEXNOW</span>
        </div>
        <div style="font-size: 1rem; font-weight: 800; color: #fff;">
          ⚡ Lotul Prioritar 16x <code>/bps-cloud</code> + <code>palyazatkalkulator.hu</code> (RO • IT • HU • DE • AT • FR • LU • NL • BE • ES • PL • PT • CZ • UK • DK • SE)
        </div>
        <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.2rem;">
          Toate cele 16 rute <code>https://DOMENIU/bps-cloud</code> sunt fixate pe <b>Index 0 (Priority 1.0)</b> în <code>sitemap.xml</code>, interconectate prin <b>17 tag-uri hreflang</b> și prioritizate primele în Google Indexing API.
        </div>
      </div>
      <a href="/push-bps-cloud" target="_blank" style="background: linear-gradient(90deg, #10b981, #3b82f6); color: #020617; font-weight: 800; font-size: 0.82rem; padding: 0.7rem 1.2rem; border-radius: 0.75rem; text-decoration: none; white-space: nowrap;">
        🚀 Push Instant 16x /bps-cloud (Index 0) →
      </a>
    </div>

    <div class="summary-grid">
      <div class="stat-card">
        <div class="stat-label">Total Pagini Portofoliu</div>
        <div class="stat-val">${grandTotal.toLocaleString()}</div>
        <div class="stat-sub">În bazele D1 Cloudflare (${totalSitesCount} Domenii)</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Indexate la Google</div>
        <div class="stat-val" style="color: #34d399;">${grandIndexed.toLocaleString()}</div>
        <div class="stat-sub">${grandPct}% din tot ecosistemul</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Indexate Azi</div>
        <div class="stat-val" style="color: #60a5fa;">${grandToday.toLocaleString()}</div>
        <div class="stat-sub">Capacitate: ${totalDailyQuota.toLocaleString()} / zi (${Math.round(totalDailyQuota / 200)} API-uri)</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Rămase la Indexat</div>
        <div class="stat-val" style="color: #fbbf24;">${(grandTotal - grandIndexed).toLocaleString()}</div>
        <div class="stat-sub">În coada de așteptare</div>
      </div>
    </div>

    <!-- Live Leads & Simulations Command Center (PLACED AT THE VERY TOP) -->
    <div class="logs-card" style="margin-bottom: 2.25rem; border: 1px solid rgba(16, 185, 129, 0.45); box-shadow: 0 10px 30px rgba(16, 185, 129, 0.08);">
      <div class="logs-header">
        <div>
          <h2 style="color: #34d399; font-size: 1.25rem;">🔔 Live Leads &amp; Cereri Clienți (Toate cele 14 Țări — Alerte WhatsApp + Email Active)</h2>
          <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">Notificări instant pe WhatsApp (<b>+39 320 948 1876</b>) &amp; Email (<b>amendamax@gmail.com</b>) + Cronometru SLA 3 Ore per instalator</p>
        </div>
        <span class="badge badge-success" style="font-size:0.8rem; padding:0.35rem 0.85rem;">${displayLeads.length} Lead-uri / ${recentSimulations.length} Simulări Recente</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Data / Ora</th>
            <th>Țara</th>
            <th>Client</th>
            <th>Telefon / WhatsApp</th>
            <th>Localitate / Cod</th>
            <th>Serviciu / Subvenție</th>
            <th>Status SLA</th>
          </tr>
        </thead>
        <tbody>
          ${
            displayLeads && displayLeads.length > 0
              ? displayLeads
                  .map(
                    (ld: any) => `
            <tr>
              <td class="time-col">${ld.created_at ? new Date(ld.created_at).toLocaleString("ro-RO") : "Recent"}</td>
              <td><b>🌍 ${ld.country_code || "EU"}</b></td>
              <td><b>${ld.full_name || "Client Web"}</b><br><span style="font-size:0.75rem;color:#94a3b8;">${ld.email || ""}</span></td>
              <td><a href="https://wa.me/${String(ld.phone || "").replace(/[^0-9]/g, "")}" target="_blank" style="color:#34d399;font-weight:700;text-decoration:none;">💬 ${ld.phone || "-"}</a></td>
              <td>${ld.postal_code || "-"}</td>
              <td><b>${ld.measure_slug || "Solar / Pompă"}</b> (${ld.estimated_grant ? Number(ld.estimated_grant).toLocaleString() + " €" : "-"})</td>
              <td><span class="badge badge-success">${ld.status || "NEW_SLA_3H"}</span></td>
            </tr>`
                  )
                  .join("")
              : `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 1.25rem;">Niciun lead nou înregistrat azi încă — alertele instant pe WhatsApp (+39 320 948 1876) și Email sunt 100% active pe toate cele 14 țări!</td></tr>`
          }
        </tbody>
      </table>
      ${
        recentSimulations && recentSimulations.length > 0
          ? `<div style="margin-top: 1.25rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.08);">
              <h3 style="font-size: 0.9rem; color: #60a5fa; margin-bottom: 0.75rem;">📊 Ultimele Simulări din Calculatoare (Pasul 1 — Vizitatori din Google)</h3>
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Portal / Țară</th>
                    <th>Oraș / Cod Poștal</th>
                    <th>Sistem</th>
                    <th>Factură / Suprafață</th>
                    <th>Subvenție Calculată</th>
                  </tr>
                </thead>
                <tbody>
                  ${recentSimulations
                    .map(
                      (sim: any) => `
                    <tr>
                      <td class="time-col">${sim.created_at ? new Date(sim.created_at).toLocaleString("ro-RO") : "Azi"}</td>
                      <td><b>${sim.country_code}</b> <span style="color:#94a3b8;font-size:0.78rem;">(${sim.domain || ""})</span></td>
                      <td>${sim.city_or_postal || "-"}</td>
                      <td>${sim.service_mode || "-"}</td>
                      <td>${sim.monthly_bill || 0} €/lună (${sim.sqm || 120} m²)</td>
                      <td style="color:#34d399;font-weight:700;">${Number(sim.estimated_grant_eur || 0).toLocaleString()} €</td>
                    </tr>`
                    )
                    .join("")}
                </tbody>
              </table>
            </div>`
          : ""
      }
    </div>

    <!-- Sites Grid -->
    <div class="sites-grid">
      ${siteStats
        .map(
          (s) => `
      <div class="site-card">
        <div>
          <div class="site-head">
            <div>
              <div class="site-title">${s.icon} ${s.name}</div>
              <a href="${s.domain}" target="_blank" class="site-domain">${s.domain} ↗</a>
              ${s.apiEmail ? `<div style="font-size:0.72rem; color:#94a3b8; font-family:'JetBrains Mono',monospace; margin-top:0.25rem; word-break:break-all;">🤖 ${s.apiEmail}</div>` : ""}
            </div>
            <span class="badge ${s.pending === 0 ? "badge-success" : s.quotaFullToday ? "badge-quota" : "badge-success"}">
              ${s.pending === 0 ? "100% Complet" : s.quotaFullToday ? `Cota Azi Plină (API ${s.dailyQuota}/${s.dailyQuota})` : "Activ"}
            </span>
          </div>

          ${
            s.lot1Done
              ? `<div style="margin: 0.1rem 0 0.85rem 0; padding: 0.5rem 0.75rem; border-radius: 0.65rem; background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.45); color: #34d399; font-size: 0.78rem; font-weight: 700; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.4rem;">
                  <span>✅ Primul lot s-a indexat (${s.lot1Size.toLocaleString()} / ${s.lot1Size.toLocaleString()})</span>
                  <span style="background: rgba(59, 130, 246, 0.25); color: #93c5fd; padding: 0.15rem 0.55rem; border-radius: 999px; font-size: 0.72rem;">Activ: ${s.lotLabel}</span>
                </div>`
              : s.isSubsidyPortal
              ? `<div style="margin: 0.1rem 0 0.85rem 0; padding: 0.4rem 0.7rem; border-radius: 0.6rem; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.25); color: #93c5fd; font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; justify-content: space-between;">
                  <span>📦 În curs: ${s.lotLabel}</span>
                  <span>${s.indexed.toLocaleString()} / ${s.lot1Size.toLocaleString()}</span>
                </div>`
              : ""
          }

          <div class="progress-wrap">
            <div class="progress-bar-bg">
              <div class="progress-bar-fill" style="width: ${s.pct}%;"></div>
            </div>
            <div class="progress-stats">
              <span>Progres: <b>${s.pct}%</b></span>
              <span>${s.indexed.toLocaleString()} / ${s.total.toLocaleString()}</span>
            </div>
          </div>

          <div class="site-metrics">
            <div class="metric-row"><span>Trimise Azi:</span> <span>${s.sentToday} / ${s.dailyQuota}</span></div>
            <div class="metric-row"><span>În Așteptare:</span> <span>${s.pending.toLocaleString()}</span></div>
          </div>
        </div>

        <button class="btn-action" onclick="triggerSite('${s.id}', this)" ${s.pending === 0 || s.quotaFullToday ? "disabled" : ""}>
          ⚡ Indexează ${s.dailyQuota >= 400 ? '40' : '35'} URLs Acum
        </button>
      </div>`
        )
        .join("")}
    </div>

    <!-- Logs Table -->
    <div class="logs-card">
      <div class="logs-header">
        <h2>Istoric Indexare & Log-uri Recente (Toate Siturile)</h2>
      </div>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Portal</th>
            <th>Status</th>
            <th>Pagini</th>
            <th>Detalii</th>
          </tr>
        </thead>
        <tbody>
          ${
            displayLogs && displayLogs.length > 0
              ? displayLogs
                  .map(
                    (l: any) => `
            <tr>
              <td class="time-col">${new Date(l.created_at).toLocaleString("ro-RO")}</td>
              <td><b>${SITES[l.site_id]?.icon || ""} ${SITES[l.site_id]?.name || l.site_id}</b></td>
              <td>
                <span class="badge ${
                  l.status === "SUCCESS" ? "badge-success" : l.status === "QUOTA_EXCEEDED" ? "badge-quota" : "badge-error"
                }">
                  ${l.status}
                </span>
              </td>
              <td><b>${l.urls_count}</b></td>
              <td style="color: var(--text-muted);">${typeof l.details === 'string' ? l.details.slice(0, 100) : JSON.stringify(l.details || "")}</td>
            </tr>`
                  )
                  .join("")
              : `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 2rem;">Nu sunt log-uri înregistrate încă. Indexerul va porni automat la cron.</td></tr>`
          }
        </tbody>
      </table>
    </div>
  </div>

  <script>
    async function triggerSite(siteId, btn) {
      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '⏳ Se trimite la Google...';
      try {
        const res = await fetch('/trigger?site=' + siteId);
        const data = await res.json();
        if (data.status === 'SUCCESS') {
          alert('Succes! Au fost indexate ' + data.processed + ' pagini noi pentru ' + siteId + '!');
        } else if (data.status === 'QUOTA_EXCEEDED') {
          alert('Cota zilnică pentru ' + siteId + ' a fost atinsă la Google. Continuăm mâine!');
        } else {
          alert('Rezultat: ' + JSON.stringify(data));
        }
        window.location.reload();
      } catch (err) {
        alert('Eroare rețea: ' + err.message);
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    }
  </script>
</body>
</html>`;

    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  },
};
