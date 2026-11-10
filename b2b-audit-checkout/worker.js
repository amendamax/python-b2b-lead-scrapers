/**
 * VasileDev Group — B2B Instant Audit Checkout & Encrypted Vault Worker
 * EU VIES VAT: IT04226190041 | PayPal Business: amendamax@gmail.com
 */

const PAYPAL_BUSINESS = "amendamax@gmail.com";
const FRONTEND_AUDIT_URL = "https://vasiledev.com/audit/";
const ADMIN_TOKEN = "vd_sec_vault_2026_98f4a17e82b941c09d3e8a";

const BOT_UA_RE = /bot|crawl|spider|slurp|bingpreview|facebookexternalhit|whatsapp|telegrambot|slackbot|discordbot|headless|lighthouse|curl|wget|python-requests/i;

function corsHeaders(origin) {
  const allowed = origin && (origin.includes("vasiledev.com") || origin.includes("localhost") || origin.includes("127.0.0.1"))
    ? origin
    : "https://vasiledev.com";
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Token",
    "Cache-Control": "no-store",
  };
}

function jsonResp(data, status = 200, origin = "") {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(origin),
    },
  });
}

function randomHex(len) {
  const arr = new Uint8Array(Math.ceil(len / 2));
  crypto.getRandomValues(arr);
  return Array.from(arr, (b) => b.toString(16).padStart(2, "0")).join("").slice(0, len);
}

function cleanDomain(raw) {
  if (!raw) return "";
  return String(raw)
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\//, "")
    .replace(/^www\./, "")
    .split("/")[0]
    .split("?")[0];
}

function base64ToUint8Array(b64) {
  const bin = atob(b64);
  const len = bin.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = bin.charCodeAt(i);
  }
  return bytes;
}

async function verifyPayPalAndUnlock(rawBody, fallbackOrderId, env) {
  if (!rawBody || !rawBody.includes("payment_status")) {
    return { verified: false, reason: "no_payment_payload" };
  }

  // Verify cryptographically against PayPal Production IPN endpoint
  const verifyResp = await fetch("https://ipnpb.paypal.com/cgi-bin/webscr", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "User-Agent": "VasileDev-Cloudflare-IPN/2.0",
    },
    body: "cmd=_notify-validate&" + rawBody,
  });
  const verifyText = (await verifyResp.text()).trim();
  if (verifyText !== "VERIFIED") {
    return { verified: false, reason: "paypal_not_verified:" + verifyText };
  }

  const params = new URLSearchParams(rawBody);
  const receiver = (params.get("receiver_email") || params.get("business") || "").trim().toLowerCase();
  const paymentStatus = (params.get("payment_status") || "").trim().toLowerCase();
  const orderId = (params.get("custom") || params.get("invoice") || fallbackOrderId || "").trim();
  const txnId = (params.get("txn_id") || "").trim();
  const payerEmail = (params.get("payer_email") || "").trim();
  const gross = parseFloat(params.get("mc_gross") || params.get("payment_gross") || "0");
  const currency = (params.get("mc_currency") || "").trim().toUpperCase();

  if (receiver !== PAYPAL_BUSINESS) {
    return { verified: false, reason: "wrong_receiver:" + receiver };
  }
  if (!["completed", "processed"].includes(paymentStatus)) {
    return { verified: false, reason: "payment_status:" + paymentStatus };
  }
  if (!orderId) {
    return { verified: false, reason: "missing_order_id" };
  }

  const order = await env.DB.prepare(
    "SELECT id, order_id, amount, currency, status FROM b2b_audit_orders WHERE order_id = ?"
  ).bind(orderId).first();

  if (!order) {
    return { verified: false, reason: "order_not_found:" + orderId };
  }
  if (currency && currency !== String(order.currency).toUpperCase()) {
    return { verified: false, reason: "currency_mismatch:" + currency };
  }
  if (gross < Number(order.amount) - 0.5) {
    return { verified: false, reason: "underpaid:" + gross };
  }

  await env.DB.prepare(
    "UPDATE b2b_audit_orders SET status = 'PAID', txn_id = ?, payer_email = ?, paid_at = CURRENT_TIMESTAMP WHERE order_id = ?"
  ).bind(txnId, payerEmail, orderId).run();

  return { verified: true, orderId, txnId };
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const path = url.pathname;

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    // 1. GET /api/shop?domain=<domain>
    if (path === "/api/shop" && request.method === "GET") {
      const dom = cleanDomain(url.searchParams.get("domain") || url.searchParams.get("shop"));
      if (!dom) {
        return jsonResp({ error: "Missing shop domain parameter." }, 400, origin);
      }

      const rawMeta = await env.B2B_AUDIT_VAULT.get("meta:" + dom);
      if (!rawMeta) {
        return jsonResp({ error: "Audit package not found for domain: " + dom }, 404, origin);
      }

      const ua = request.headers.get("User-Agent") || "";
      const skipLog = url.searchParams.get("preview") === "1" || BOT_UA_RE.test(ua);
      if (!skipLog) {
        const country = (request.cf && request.cf.country) ? String(request.cf.country) : "";
        const city = (request.cf && request.cf.city) ? String(request.cf.city) : "";
        ctx.waitUntil(
          env.DB.prepare("INSERT INTO b2b_audit_views (domain, country, city, ua) VALUES (?, ?, ?, ?)")
            .bind(dom, country, city, ua.slice(0, 180))
            .run()
            .catch(() => {})
        );
      }

      return jsonResp({ ok: true, shop: JSON.parse(rawMeta) }, 200, origin);
    }

    // 2. POST /api/create-order
    if (path === "/api/create-order" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return jsonResp({ error: "Invalid JSON payload." }, 400, origin);
      }

      const dom = cleanDomain(body.domain);
      const rawMeta = dom ? await env.B2B_AUDIT_VAULT.get("meta:" + dom) : null;
      if (!rawMeta) {
        return jsonResp({ error: "Unknown store domain." }, 404, origin);
      }
      const meta = JSON.parse(rawMeta);
      const tier = body.tier === "opt2" ? "opt2" : "opt1";
      const amount = tier === "opt2" ? Number(meta.pricing.flash_opt2) : Number(meta.pricing.flash_opt1);
      const currency = String(meta.pricing.currency || "EUR").toUpperCase();

      const companyName = String(body.company_name || meta.company_name || dom).trim().slice(0, 140);
      const vatId = String(body.vat_id || meta.vat_id || "").trim().slice(0, 50);
      const buyerEmail = String(body.buyer_email || meta.email || "").trim().slice(0, 140);

      // Deduplicate rapid repeated clicks / corporate sandbox clicks within 15 minutes
      const existingPending = await env.DB.prepare(
        `SELECT order_id, access_secret FROM b2b_audit_orders
         WHERE domain = ? AND tier = ? AND status = 'PENDING'
           AND created_at >= datetime('now', '-15 minutes')
         ORDER BY id DESC LIMIT 1`
      ).bind(dom, tier).first();

      let orderId;
      let accessSecret;
      if (existingPending && existingPending.order_id && existingPending.access_secret) {
        orderId = existingPending.order_id;
        accessSecret = existingPending.access_secret;
        await env.DB.prepare(
          "UPDATE b2b_audit_orders SET company_name = ?, vat_id = ?, buyer_email = ? WHERE order_id = ?"
        ).bind(companyName, vatId, buyerEmail, orderId).run();
      } else {
        orderId = "BF26-" + randomHex(8).toUpperCase();
        accessSecret = randomHex(24);
        await env.DB.prepare(
          `INSERT INTO b2b_audit_orders
           (order_id, access_secret, domain, tier, amount, currency, company_name, vat_id, buyer_email, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')`
        ).bind(orderId, accessSecret, dom, tier, amount, currency, companyName, vatId, buyerEmail).run();
      }

      const workerOrigin = url.origin;
      const itemName = tier === "opt2"
        ? `30-Day Live Black Friday Price Radar + Full Excel Matrix - ${dom}`
        : `Black Friday Full Price & Stock Matrix (.XLSX + ERP Import) - ${dom}`;

      const pp = new URL("https://www.paypal.com/cgi-bin/webscr");
      pp.searchParams.set("cmd", "_xclick");
      pp.searchParams.set("business", PAYPAL_BUSINESS);
      pp.searchParams.set("item_name", itemName);
      pp.searchParams.set("item_number", dom);
      pp.searchParams.set("custom", orderId);
      pp.searchParams.set("invoice", orderId);
      pp.searchParams.set("amount", amount.toFixed(2));
      pp.searchParams.set("currency_code", currency);
      pp.searchParams.set("no_shipping", "1");
      pp.searchParams.set("no_note", "1");
      pp.searchParams.set("charset", "utf-8");
      pp.searchParams.set("landing_page", "billing");
      pp.searchParams.set("rm", "2");
      pp.searchParams.set("notify_url", `${workerOrigin}/api/paypal-ipn`);
      pp.searchParams.set(
        "return",
        `${workerOrigin}/api/paypal-return?shop=${encodeURIComponent(dom)}&order=${encodeURIComponent(orderId)}&key=${encodeURIComponent(accessSecret)}`
      );
      pp.searchParams.set(
        "cancel_return",
        `${FRONTEND_AUDIT_URL}?shop=${encodeURIComponent(dom)}&cancelled=1`
      );

      return jsonResp({
        ok: true,
        order_id: orderId,
        access_secret: accessSecret,
        amount,
        currency,
        paypal_url: pp.toString(),
      }, 200, origin);
    }

    // 3. POST /api/paypal-ipn (Official Server-to-Server PayPal IPN Webhook)
    if (path === "/api/paypal-ipn" && request.method === "POST") {
      const rawBody = await request.text();
      await verifyPayPalAndUnlock(rawBody, "", env);
      return new Response("OK", { status: 200 });
    }

    // 4. GET or POST /api/paypal-return (Handles PayPal rm=2 POST redirect & bounces cleanly via 303 GET to vasiledev.com/audit/)
    if (path === "/api/paypal-return") {
      const dom = cleanDomain(url.searchParams.get("shop"));
      const orderId = (url.searchParams.get("order") || "").trim();
      const key = (url.searchParams.get("key") || "").trim();

      if (request.method === "POST") {
        try {
          const rawBody = await request.text();
          if (rawBody && rawBody.includes("payment_status")) {
            await verifyPayPalAndUnlock(rawBody, orderId, env);
          }
        } catch {}
      }

      const target = `${FRONTEND_AUDIT_URL}?shop=${encodeURIComponent(dom)}&order=${encodeURIComponent(orderId)}&key=${encodeURIComponent(key)}&paid_return=1`;
      return Response.redirect(target, 303);
    }

    // 5. GET /api/order-status?order=...&key=...
    if (path === "/api/order-status" && request.method === "GET") {
      const orderId = (url.searchParams.get("order") || "").trim();
      const key = (url.searchParams.get("key") || "").trim();
      if (!orderId || !key) {
        return jsonResp({ error: "Missing order credentials." }, 400, origin);
      }

      const row = await env.DB.prepare(
        `SELECT id, order_id, domain, tier, amount, currency, company_name, vat_id, buyer_email,
                status, txn_id, payer_email, download_count, created_at, paid_at
         FROM b2b_audit_orders WHERE order_id = ? AND access_secret = ?`
      ).bind(orderId, key).first();

      if (!row) {
        return jsonResp({ error: "Order not found." }, 404, origin);
      }

      return jsonResp({
        ok: true,
        order: {
          ...row,
          invoice_no: `VD-2026-${String(1000 + Number(row.id))}`,
        },
      }, 200, origin);
    }

    // 6. GET /api/download-xlsx?order=...&key=...
    if (path === "/api/download-xlsx" && request.method === "GET") {
      const orderId = (url.searchParams.get("order") || "").trim();
      const key = (url.searchParams.get("key") || "").trim();
      if (!orderId || !key) {
        return jsonResp({ error: "Missing download credentials." }, 403, origin);
      }

      const row = await env.DB.prepare(
        "SELECT order_id, domain, status FROM b2b_audit_orders WHERE order_id = ? AND access_secret = ?"
      ).bind(orderId, key).first();

      if (!row || row.status !== "PAID") {
        return jsonResp({ error: "Payment verification pending or unauthorized." }, 403, origin);
      }

      const b64 = await env.B2B_AUDIT_VAULT.get("xlsx:" + row.domain);
      if (!b64) {
        return jsonResp({ error: "Audit file missing from vault." }, 404, origin);
      }

      ctx.waitUntil(
        env.DB.prepare("UPDATE b2b_audit_orders SET download_count = download_count + 1 WHERE order_id = ?")
          .bind(orderId)
          .run()
          .catch(() => {})
      );

      const bytes = base64ToUint8Array(b64);
      const fileName = `Full_Audit_BlackFriday_${row.domain}.xlsx`;
      return new Response(bytes, {
        status: 200,
        headers: {
          "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "Content-Disposition": `attachment; filename="${fileName}"`,
          ...corsHeaders(origin),
        },
      });
    }

    // 7. Admin Live Monitor & Manual/IMAP Watcher Unlock
    if (path === "/api/admin/live" && request.method === "GET") {
      const tok = url.searchParams.get("token") || request.headers.get("X-Admin-Token") || "";
      if (tok !== ADMIN_TOKEN) {
        return jsonResp({ error: "Forbidden" }, 403, origin);
      }
      const views = await env.DB.prepare(
        "SELECT id, domain, country, city, ua, created_at FROM b2b_audit_views ORDER BY id DESC LIMIT 80"
      ).all();
      const orders = await env.DB.prepare(
        "SELECT id, order_id, access_secret, domain, tier, amount, currency, company_name, vat_id, buyer_email, status, txn_id, payer_email, download_count, created_at, paid_at FROM b2b_audit_orders ORDER BY id DESC LIMIT 50"
      ).all();
      return jsonResp({
        ok: true,
        views: views.results || [],
        orders: orders.results || [],
      }, 200, origin);
    }

    if (path === "/api/admin/revoke-false-imap" && request.method === "POST") {
      const tok = url.searchParams.get("token") || request.headers.get("X-Admin-Token") || "";
      if (tok !== ADMIN_TOKEN) {
        return jsonResp({ error: "Forbidden" }, 403, origin);
      }
      const res = await env.DB.prepare(
        "UPDATE b2b_audit_orders SET status = 'PENDING', txn_id = NULL, paid_at = NULL WHERE txn_id = 'PAYPAL-IMAP-VERIFIED'"
      ).run();
      return jsonResp({ ok: true, changes: res.meta ? res.meta.changes : 0 }, 200, origin);
    }

    if (path === "/api/admin/mark-paid" && request.method === "POST") {
      const tok = url.searchParams.get("token") || request.headers.get("X-Admin-Token") || "";
      if (tok !== ADMIN_TOKEN) {
        return jsonResp({ error: "Forbidden" }, 403, origin);
      }
      const body = await request.json();
      const orderId = String(body.order_id || "").trim();
      const txnId = String(body.txn_id || "MANUAL-PAYPAL-VERIFIED").trim();
      const payerEmail = String(body.payer_email || "").trim();
      await env.DB.prepare(
        "UPDATE b2b_audit_orders SET status = 'PAID', txn_id = ?, payer_email = ?, paid_at = CURRENT_TIMESTAMP WHERE order_id = ?"
      ).bind(txnId, payerEmail, orderId).run();
      return jsonResp({ ok: true, order_id: orderId, status: "PAID" }, 200, origin);
    }

    return jsonResp({ service: "VasileDev B2B Audit Vault", status: "online" }, 200, origin);
  },
};
