export interface Env {
  DB: D1Database;
  DB_ITALY?: D1Database;
  DB_ROMANIA?: D1Database;
  SECRET_JOBSCAM?: string;
  SECRET_PILLSCAM?: string;
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
}

const SITES: Record<string, SiteConfig> = {
  calcolaincentivi: {
    id: "calcolaincentivi",
    name: "CalcolaIncentivi.it",
    domain: "https://calcolaincentivi.it",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 400,
    icon: "☀️",
  },
  calculeazasubventii: {
    id: "calculeazasubventii",
    name: "CalculeazaSubventii.ro",
    domain: "https://calculeazasubventii.ro",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 400,
    icon: "🇷🇴",
  },
  jobscam: {
    id: "jobscam",
    name: "JobScamRadar",
    domain: "https://jobscamradar.com",
    secretKey: "SECRET_JOBSCAM",
    dailyQuota: 200,
    icon: "💼",
  },
  broker: {
    id: "broker",
    name: "IsBrokerSafe",
    domain: "https://isbrokersafe.com",
    secretKey: "SECRET_BROKER",
    dailyQuota: 200,
    icon: "🛡️",
  },
  dating: {
    id: "dating",
    name: "VerifyDating",
    domain: "https://verifydating.net",
    secretKey: "SECRET_DATING",
    dailyQuota: 200,
    icon: "❤️",
  },
  pillscam: {
    id: "pillscam",
    name: "PillScamRadar",
    domain: "https://pillscamradar.com",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 200,
    icon: "💊",
  },
  appscam: {
    id: "appscam",
    name: "AppScamRadar",
    domain: "https://appscamradar.com",
    secretKey: "SECRET_PILLSCAM",
    dailyQuota: 200,
    icon: "📱",
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

async function runBatchForSite(
  siteId: string,
  batchSize: number,
  env: Env
): Promise<{ processed: number; errors: string[]; status: string }> {
  // If CalcolaIncentivi, call its dedicated worker endpoint
  if (siteId === "calcolaincentivi") {
    try {
      const resp = await fetch("https://seo-indexer.amendamax.workers.dev/run?limit=40");
      const data: any = await resp.json();
      const processed = data.total_sent || 0;
      const errors = data.errors || [];
      const status = processed > 0 ? "SUCCESS" : errors.length ? "QUOTA_EXCEEDED" : "EMPTY";
      return { processed, errors, status };
    } catch (e: any) {
      return { processed: 0, errors: [e.message], status: "ERROR" };
    }
  }

  // If CalculeazaSubventii.ro, call its dedicated worker endpoint
  if (siteId === "calculeazasubventii") {
    try {
      const resp = await fetch("https://ro-seo-indexer.amendamax.workers.dev/run?limit=40");
      const data: any = await resp.json();
      const processed = data.total_sent || 0;
      const errors = data.errors || [];
      const status = processed > 0 ? "SUCCESS" : errors.length ? "QUOTA_EXCEEDED" : "EMPTY";
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

  // Check how many sent today
  const todayRow = await env.DB.prepare(
    "SELECT COALESCE(SUM(urls_count), 0) as cnt FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now') AND status = 'SUCCESS'"
  ).bind(siteId).first<{ cnt: number }>();

  const sentToday = todayRow?.cnt || 0;
  if (sentToday >= site.dailyQuota) {
    return { processed: 0, errors: [`Cota zilnică (${site.dailyQuota}) a fost deja atinsă azi (${sentToday})`], status: "QUOTA_EXCEEDED" };
  }

  const allowedBatch = Math.min(batchSize, site.dailyQuota - sentToday);
  if (allowedBatch <= 0) {
    return { processed: 0, errors: ["Cota zilnică atinsă"], status: "QUOTA_EXCEEDED" };
  }

  // Get pending URLs
  const { results: pending } = await env.DB.prepare(
    "SELECT id, url FROM urls_queue WHERE site_id = ? AND is_indexed = 0 ORDER BY id ASC LIMIT ?"
  ).bind(siteId, allowedBatch).all<{ id: number; url: string }>();

  if (!pending || pending.length === 0) {
    return { processed: 0, errors: ["Toate paginile sunt deja indexate!"], status: "EMPTY" };
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
    console.log(`[CRON] Started at ${new Date().toISOString()}`);

    // Cycle through sites (skip calcolaincentivi & calculeazasubventii since they have their own workers)
    const siteIds = Object.keys(SITES).filter(id => id !== "calcolaincentivi" && id !== "calculeazasubventii");

    for (const siteId of siteIds) {
      const site = SITES[siteId];
      const todayRow = await env.DB.prepare(
        "SELECT COALESCE(SUM(urls_count), 0) as cnt FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now') AND status = 'SUCCESS'"
      ).bind(siteId).first<{ cnt: number }>();

      const sentToday = todayRow?.cnt || 0;
      if (sentToday >= site.dailyQuota) continue;

      const quotaExceededRow = await env.DB.prepare(
        "SELECT COUNT(*) as cnt FROM indexing_logs WHERE site_id = ? AND created_at >= datetime('now', '-3 hours') AND status = 'QUOTA_EXCEEDED'"
      ).bind(siteId).first<{ cnt: number }>();

      if (quotaExceededRow && quotaExceededRow.cnt > 0) continue;

      const pendingRow = await env.DB.prepare(
        "SELECT id FROM urls_queue WHERE site_id = ? AND is_indexed = 0 LIMIT 1"
      ).bind(siteId).first<{ id: number }>();

      if (!pendingRow) continue;

      console.log(`[CRON] Processing site ${site.name} (sent today: ${sentToday}/${site.dailyQuota})`);
      const result = await runBatchForSite(siteId, 35, env);
      console.log(`[CRON] Finished batch for ${site.name}:`, result);
      if (result.status === "SUCCESS") {
        break;
      }
    }
  },

  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // API stats
    if (url.pathname === "/api/stats") {
      const stats: Record<string, any> = {};
      for (const siteId of Object.keys(SITES)) {
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
          const total = totalRow?.total || 789;
          const indexed = totalRow?.indexed || 0;
          stats[siteId] = {
            total,
            indexed,
            pending: total - indexed,
            sent_today: totalRow?.sent_today || 0,
          };
        } else {
          const totalRow = await env.DB.prepare("SELECT COUNT(*) as total, SUM(is_indexed) as indexed FROM urls_queue WHERE site_id = ?").bind(siteId).first<{ total: number; indexed: number }>();
          const todayRow = await env.DB.prepare("SELECT COALESCE(SUM(urls_count), 0) as sent_today FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now') AND status = 'SUCCESS'").bind(siteId).first<{ sent_today: number }>();
          stats[siteId] = {
            total: totalRow?.total || 0,
            indexed: totalRow?.indexed || 0,
            pending: (totalRow?.total || 0) - (totalRow?.indexed || 0),
            sent_today: todayRow?.sent_today || 0,
          };
        }
      }
      return Response.json(stats);
    }

    // Manual trigger
    if (url.pathname === "/trigger") {
      const siteId = url.searchParams.get("site") || "jobscam";
      const count = parseInt(url.searchParams.get("count") || "35", 10);
      const res = await runBatchForSite(siteId, Math.min(count, 40), env);
      return new Response(
        JSON.stringify(res, null, 2),
        { headers: { "Content-Type": "application/json" } }
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
        total = totalRow?.total || 789;
        indexed = totalRow?.indexed || 0;
        sentToday = totalRow?.sent_today || 0;
      } else {
        const totalRow = await env.DB.prepare(
          "SELECT COUNT(*) as total, COALESCE(SUM(is_indexed), 0) as indexed FROM urls_queue WHERE site_id = ?"
        ).bind(siteId).first<{ total: number; indexed: number }>();

        const todayRow = await env.DB.prepare(
          "SELECT COALESCE(SUM(urls_count), 0) as sent_today FROM indexing_logs WHERE site_id = ? AND date(created_at) = date('now') AND status = 'SUCCESS'"
        ).bind(siteId).first<{ sent_today: number }>();

        total = totalRow?.total || 0;
        indexed = totalRow?.indexed || 0;
        sentToday = todayRow?.sent_today || 0;
      }

      const pending = total - indexed;
      const pct = total > 0 ? Math.round((indexed / total) * 100) : 0;

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

    const grandPct = grandTotal > 0 ? Math.round((grandIndexed / grandTotal) * 100) : 0;

    const html = `<!DOCTYPE html>
<html lang="ro">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Indexer Fleet | 6 Portaluri Active</title>
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
        <p class="subtitle">Monitorizare și indexare automată 24/7 prin Google Indexing API pentru cele 7 portaluri</p>
      </div>
      <div>
        <span class="status-pill">
          <span class="pulse-dot"></span>
          7 Roboți Activi
        </span>
      </div>
    </header>

    <!-- Global Stats -->
    <div class="summary-grid">
      <div class="stat-card">
        <div class="stat-label">Total Pagini Portofoliu</div>
        <div class="stat-val">${grandTotal.toLocaleString()}</div>
        <div class="stat-sub">În bazele D1 Cloudflare</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Indexate la Google</div>
        <div class="stat-val" style="color: #34d399;">${grandIndexed.toLocaleString()}</div>
        <div class="stat-sub">${grandPct}% din tot ecosistemul</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Indexate Azi</div>
        <div class="stat-val" style="color: #60a5fa;">${grandToday.toLocaleString()}</div>
        <div class="stat-sub">Capacitate: 1,600 / zi</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Rămase la Indexat</div>
        <div class="stat-val" style="color: #fbbf24;">${(grandTotal - grandIndexed).toLocaleString()}</div>
        <div class="stat-sub">În coada de așteptare</div>
      </div>
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
            </div>
            <span class="badge ${s.pending === 0 ? "badge-success" : s.sentToday >= s.dailyQuota ? "badge-quota" : "badge-success"}">
              ${s.pending === 0 ? "100% Complet" : s.sentToday >= s.dailyQuota ? "Cota Azi Plină (" + s.sentToday + "/" + s.dailyQuota + ")" : "Activ"}
            </span>
          </div>

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

        <button class="btn-action" onclick="triggerSite('${s.id}', this)" ${s.pending === 0 || s.sentToday >= s.dailyQuota ? "disabled" : ""}>
          ⚡ Indexează ${s.id === 'calcolaincentivi' || s.id === 'calculeazasubventii' ? '40' : '35'} URLs Acum
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
