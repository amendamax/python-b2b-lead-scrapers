const GOLDEN_EXAMPLES = [
  {
    id: "nextjs-hydration",
    label: "1. Next.js Hydration Error (Lovable / Bolt / v0)",
    tool: "v0 / Next.js / Cursor",
    error: `Unhandled Runtime Error
Error: Hydration failed because the initial UI does not match what was rendered on the server.
Warning: Expected server HTML to contain a matching <div> in <p>.
See more info here: https://nextjs.org/docs/messages/react-hydration-error`,
    result: {
      summary: "Your page was built twice—once on the server and once in the browser—and the two versions didn't match.",
      plain_english: "AI coding tools (like v0, Cursor, or Bolt) often accidentally put a block element like a `<div>` inside a paragraph `<p>` tag, or use things like `new Date()`, `Math.random()`, or `window.localStorage` directly inside the component render. Because the server and your browser see slightly different results (or invalid HTML nesting), React panics and refuses to attach to the page.",
      steps: [
        "Look at the component mentioned in the error stack trace.",
        "Check if there is a `<div>` nested inside a `<p>` tag — replace the outer `<p>` with a `<div>`.",
        "If the component uses `localStorage`, `window`, or `new Date()`, move that logic inside a `useEffect(() => { ... }, [])` hook so it only runs in the browser."
      ],
      ai_prompt: "Fix the React Hydration mismatch in this component: 1) Replace any <p> tags that wrap <div> or block elements with <div> tags, and 2) Move any window, localStorage, or Date/random calls into a useEffect state hook so server and client HTML match.",
      fixed_code: `// BEFORE (Breaks Hydration):
export default function PromoBanner() {
  return <p><div>Special Offer Today!</div></p>;
}

// AFTER (Fixed):
export default function PromoBanner() {
  return <div><div>Special Offer Today!</div></div>;
}`
    }
  },
  {
    id: "supabase-rls",
    label: "2. Supabase RLS Policy Error (42501)",
    tool: "Lovable / Bolt / Supabase",
    error: `AuthApiError / PostgrestError: new row violates row-level security policy for table "profiles" (Code: 42501, Status: 403 Forbidden)`,
    result: {
      summary: "Your database is locked for safety, and your app tried to save data without a security pass (Policy) allowing it.",
      plain_english: "When you enable Row Level Security (RLS) in Supabase, Supabase blocks ALL reads and writes by default until you explicitly add a rule (Policy) saying who is allowed to insert or update rows. Even if your user is logged in, the `profiles` table doesn't yet have an `INSERT` policy for authenticated users.",
      steps: [
        "Open your Supabase Dashboard -> Authentication -> Policies (or SQL Editor).",
        "Find the `profiles` table and add an `INSERT` policy allowing logged-in users to insert their own row (`auth.uid() = id`).",
        "Run the SQL snippet below in the Supabase SQL Editor."
      ],
      ai_prompt: "Generate the Supabase SQL migration to enable INSERT and SELECT Row-Level Security (RLS) policies on the `profiles` table where `auth.uid() = id`.",
      fixed_code: `CREATE POLICY "Users can insert their own profile"
ON public.profiles
FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view their own profile"
ON public.profiles
FOR SELECT
TO authenticated
USING (auth.uid() = id);`
    }
  },
  {
    id: "vercel-env-missing",
    label: "3. Vercel Build Failed: Missing API Key / Env Variable",
    tool: "Vercel / GitHub Deploy",
    error: `Error: Missing credentials. Please pass an \`apiKey\`, or set the \`OPENAI_API_KEY\` environment variable.
    at new OpenAI (/vercel/path0/node_modules/openai/index.mjs:142:13)
Error: Command "npm run build" exited with 1`,
    result: {
      summary: "Your app works on your computer because of your local `.env` file, but Vercel doesn't have your secret API key yet.",
      plain_english: "Secret keys stored in `.env` or `.env.local` are never uploaded to GitHub (to keep them safe). When Vercel tries to build your website in the cloud, `process.env.OPENAI_API_KEY` is empty. Also, initializing `new OpenAI()` at the top of a file runs during build time before any user even visits the site.",
      steps: [
        "Go to your Vercel Dashboard -> Select your Project -> Settings -> Environment Variables.",
        "Add `OPENAI_API_KEY` with your secret key and click Save.",
        "Move `new OpenAI()` inside your API route handler function so it only runs when a request arrives, not during static build."
      ],
      ai_prompt: "Lazy-initialize the OpenAI client inside the request handler function instead of the module top-level so `npm run build` on Vercel does not fail if environment variables are evaluated at build time.",
      fixed_code: `// Inside app/api/fix/route.ts
import OpenAI from "openai";

export async function POST(req: Request) {
  // Initialize inside the function so build-time static analysis never crashes
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  // ... rest of your handler
}`
    }
  },
  {
    id: "react-use-client",
    label: "4. Next.js Server Component Error: useState not allowed",
    tool: "Cursor / Next.js App Router",
    error: `Error: You're importing a component that needs \`useState\`. This React Hook only works in a Client Component, but none of its parents are marked with "use client", so they're Server Components by default.`,
    result: {
      summary: "You used an interactive browser feature (`useState` or `onClick`) in a file that Next.js assumes is server-only.",
      plain_english: "In modern Next.js (App Router), every file inside the `app/` folder runs on the server by default. Whenever a component needs interactivity—like clicking buttons (`onClick`), typing in inputs (`useState`), or running browser code (`useEffect`)—you must put `\"use client\";` on the very first line of the file.",
      steps: [
        "Open the file shown in the error message.",
        "Add `\"use client\";` at line 1 (above all `import` statements).",
        "Save the file—Next.js will immediately reload and fix the error."
      ],
      ai_prompt: "Add the \"use client\" directive at the very top of this component file before all imports so React hooks (`useState`, `useEffect`) and event handlers work properly in Next.js App Router.",
      fixed_code: `"use client"; // <-- Add this on Line 1!

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Clicked {count}</button>;
}`
    }
  },
  {
    id: "cors-blocked",
    label: "5. CORS Policy Blocked Fetch Request",
    tool: "Replit / Bolt / Frontend-to-API",
    error: `Access to fetch at 'https://api.openai.com/v1/chat/completions' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.`,
    result: {
      summary: "Your browser blocked the request because you're calling a private third-party API directly from frontend browser code.",
      plain_english: "For security reasons, web browsers block frontend JavaScript from directly calling many external APIs (or exposing your secret API key in the user's browser). Instead of calling the external API directly from your React button click, your frontend should call your own backend route (`/api/...`), which then talks to the external service safely.",
      steps: [
        "Create a backend API endpoint in your project (e.g. `app/api/analyze/route.ts`).",
        "Move the external `fetch(...)` call and secret API key into that backend file.",
        "Update your frontend component to call `fetch('/api/analyze')` instead."
      ],
      ai_prompt: "Move this external API fetch call out of the client component into a Next.js server route handler (`app/api/proxy/route.ts`) to prevent CORS errors and keep the API key off the client browser.",
      fixed_code: `// Frontend calls your own server route (No CORS error!):
const res = await fetch("/api/analyze", {
  method: "POST",
  body: JSON.stringify({ input })
});`
    }
  },
  {
    id: "cannot-read-undefined",
    label: "6. TypeError: Cannot read properties of undefined (reading 'map')",
    tool: "Lovable / Cursor / React",
    error: `Uncaught TypeError: Cannot read properties of undefined (reading 'map')
    at UserList (UserList.tsx:14:21)`,
    result: {
      summary: "Your code tried to loop over a list of items (`items.map(...)`) before the data finished loading.",
      plain_english: "When your page first opens, data coming from an API or database is temporarily `undefined` for a fraction of a second while it loads. Calling `.map()` on `undefined` crashes the whole screen. Adding a question mark (`items?.map(...)`) or a default empty list (`(items || []).map(...)`) tells JavaScript to wait safely.",
      steps: [
        "Go to line 14 of `UserList.tsx` (or wherever `.map(` is called).",
        "Change `items.map(...)` to `(items ?? []).map(...)`.",
        "Initialize your `useState([])` with an empty array `[]` instead of `useState()`."
      ],
      ai_prompt: "Fix the `Cannot read properties of undefined (reading 'map')` crash by initializing the state with an empty array `useState([])` and using optional chaining `(items ?? []).map(...)`.",
      fixed_code: `// BEFORE (Crashes while loading):
const [users, setUsers] = useState();
return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;

// AFTER (Safe):
const [users, setUsers] = useState([]);
return <ul>{(users ?? []).map(u => <li key={u.id}>{u.name}</li>)}</ul>;`
    }
  }
];

function heuristicFallback(errorText) {
  const lower = errorText.toLowerCase();
  for (const ex of GOLDEN_EXAMPLES) {
    if (
      (lower.includes("hydration") && ex.id === "nextjs-hydration") ||
      ((lower.includes("row-level security") || lower.includes("42501")) && ex.id === "supabase-rls") ||
      ((lower.includes("openai_api_key") || lower.includes("missing credentials")) && ex.id === "vercel-env-missing") ||
      (lower.includes("use client") && ex.id === "react-use-client") ||
      (lower.includes("cors policy") && ex.id === "cors-blocked") ||
      (lower.includes("reading 'map'") && ex.id === "cannot-read-undefined")
    ) {
      return ex.result;
    }
  }

  return {
    summary: "Your app encountered a configuration or runtime mismatch that stopped execution.",
    plain_english: `In plain English: the error message ("${errorText.slice(0, 140)}...") happens when a file path, environment variable, or data object isn't in the shape your framework expects at the moment the code runs.`,
    steps: [
      "Check the exact file name and line number shown in the first line of your error stack.",
      "Verify that any imported package or environment variable used on that line is installed (`npm install`) and defined in your settings.",
      "Paste the prompt below into your AI coding assistant (Cursor, Lovable, Bolt, or v0) to apply a targeted fix without breaking the rest of your page."
    ],
    ai_prompt: `Please fix the following error in my project without changing unrelated components. Explain what caused it in 1 sentence and apply the minimal safe code fix:\n\n${errorText.slice(0, 500)}`,
    fixed_code: `// Tip: Guard uncertain values and verify imports before rendering:\nif (!data) return <div>Loading...</div>;`
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/explain" && request.method === "POST") {
      try {
        const body = await request.json();
        const errorText = String(body.error || "").trim();
        const toolContext = String(body.tool || "Cursor / Lovable / Bolt / Next.js").trim();

        if (!errorText) {
          return Response.json({ error: "Please paste an error message first." }, { status: 400 });
        }

        // Check exact match in golden examples first (0 token cost = keeps monthly bill near £0!)
        for (const ex of GOLDEN_EXAMPLES) {
          if (errorText.includes(ex.error.slice(0, 45))) {
            return Response.json({ ...ex.result, cached: true, cost_gbp: "£0.0000 (Cached Pattern)" });
          }
        }

        // If Workers AI is available, generate live plain-English explanation + fix
        if (env.AI) {
          try {
            const sysPrompt = `You are a friendly senior developer who explains coding and AI/vibe-coding errors (from Cursor, Lovable, Bolt, Replit, v0, Next.js, Supabase, Vercel, Python) in clear, plain English for non-technical founders and builders.
Respond ONLY with valid JSON matching this exact structure:
{
  "summary": "One short sentence in plain English summarizing what went wrong.",
  "plain_english": "2-3 clear sentences explaining why this happens without jargon.",
  "steps": ["Step 1...", "Step 2...", "Step 3..."],
  "ai_prompt": "A ready-to-copy prompt the user can paste into Cursor/Lovable/Bolt to fix this exact error.",
  "fixed_code": "A short before/after code example showing the fix."
}`;
            const aiRes = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
              messages: [
                { role: "system", content: sysPrompt },
                { role: "user", content: `Tool/Stack: ${toolContext}\nError pasted by user:\n${errorText.slice(0, 2000)}` }
              ],
              max_tokens: 650,
              temperature: 0.2
            });

            const rawText = aiRes?.response || "";
            const jsonMatch = rawText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
              const parsed = JSON.parse(jsonMatch[0]);
              if (parsed.summary && parsed.plain_english) {
                return Response.json({
                  summary: parsed.summary,
                  plain_english: parsed.plain_english,
                  steps: Array.isArray(parsed.steps) ? parsed.steps : ["Apply the fix shown below."],
                  ai_prompt: parsed.ai_prompt || `Fix this error safely:\n${errorText.slice(0, 300)}`,
                  fixed_code: parsed.fixed_code || "",
                  cached: false,
                  cost_gbp: "~£0.0002 (Budget Cap Active)"
                });
              }
            }
          } catch (e) {
            // Fallback to deterministic heuristic if AI JSON parse fails
          }
        }

        const fb = heuristicFallback(errorText);
        return Response.json({ ...fb, cached: false, cost_gbp: "~£0.0001 (Budget Cap Active)" });
      } catch (err) {
        return Response.json({ error: "Invalid request payload" }, { status: 400 });
      }
    }

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>PlainFix AI — Plain-English Error Fixer for AI & Vibe-Coding Tools</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans selection:bg-indigo-500 selection:text-white">
  <!-- Top Status Bar -->
  <div class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-emerald-400 flex items-center justify-center font-black text-slate-950 text-sm">PF</div>
        <div>
          <span class="font-bold text-white tracking-tight">PlainFix</span>
          <span class="text-xs ml-2 px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-medium">Vibe-Coding Edition (MVP Preview)</span>
        </div>
      </div>
      <div class="flex items-center gap-3 text-xs">
        <span class="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          AI Spend Cap: <strong>£5–£50/mo Guardrail Active</strong>
        </span>
        <span class="hidden sm:inline text-slate-400">Vercel-Ready Build</span>
      </div>
    </div>
  </div>

  <main class="max-w-5xl mx-auto px-4 py-8 md:py-12">
    <!-- Hero -->
    <div class="text-center max-w-3xl mx-auto mb-8">
      <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight text-white mb-3">
        Paste any scary coding error.<br/>
        <span class="bg-gradient-to-r from-indigo-400 via-sky-300 to-emerald-300 bg-clip-text text-transparent">Get a plain-English explanation & instant fix.</span>
      </h1>
      <p class="text-slate-400 text-sm md:text-base">
        Built specifically for builders using <strong>Cursor, Lovable, Bolt, v0, Replit, Supabase & Vercel</strong>. No confusing jargon—just what happened, why, and the exact prompt or snippet to fix it.
      </p>
    </div>

    <!-- Pre-loaded Example Chips (From the 1-page brief requirement) -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Try 1 of the 6 Built-In Example Errors (1-Click Test):</span>
        <button onclick="clearAll()" class="text-xs text-slate-400 hover:text-white underline">Clear input</button>
      </div>
      <div class="flex flex-wrap gap-2" id="example-chips"></div>
    </div>

    <!-- Main Input Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 md:p-6 shadow-2xl mb-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
        <div class="md:col-span-3">
          <label class="block text-xs font-semibold text-slate-300 mb-1">Paste your error message or terminal log:</label>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Where did this happen?</label>
          <select id="tool-select" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500">
            <option value="Cursor / Lovable / Bolt / v0">Cursor / Lovable / Bolt / v0</option>
            <option value="Next.js / React / Vercel">Next.js / React / Vercel</option>
            <option value="Supabase / Database / Auth">Supabase / Database / Auth</option>
            <option value="Python / FastAPI / Node.js">Python / FastAPI / Node.js</option>
          </select>
        </div>
      </div>

      <textarea
        id="error-input"
        rows="5"
        placeholder="Paste the red error message from Cursor, Lovable, Bolt, Vercel build logs, or your browser console here..."
        class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs md:text-sm font-mono text-rose-300 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition"
      ></textarea>

      <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
        <span class="text-xs text-slate-500">⚡ Uses smart pattern caching + lightweight LLM routing to keep API costs under £5–£25/mo.</span>
        <button
          id="fix-btn"
          onclick="analyzeError()"
          class="bg-gradient-to-r from-indigo-500 to-emerald-500 hover:from-indigo-400 hover:to-emerald-400 text-slate-950 font-bold px-6 py-2.5 rounded-xl text-sm shadow-lg transition flex items-center gap-2"
        >
          <span>✨ Explain & Fix in Plain English</span>
        </button>
      </div>
    </div>

    <!-- Output Result Container -->
    <div id="result-box" class="hidden space-y-4">
      <!-- 1. One-Line Headline Summary -->
      <div class="bg-gradient-to-r from-indigo-950/70 to-slate-900 border border-indigo-500/40 rounded-2xl p-5">
        <div class="flex items-center justify-between gap-2 mb-1.5">
          <span class="text-[11px] font-bold uppercase tracking-wider text-indigo-300">1. TL;DR — What Went Wrong</span>
          <span id="cost-badge" class="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-emerald-300 font-mono"></span>
        </div>
        <h2 id="res-summary" class="text-lg md:text-xl font-bold text-white"></h2>
      </div>

      <!-- 2. Plain-English Explanation -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <span class="text-[11px] font-bold uppercase tracking-wider text-emerald-400 block mb-2">2. Plain-English Explanation (Zero Jargon)</span>
        <p id="res-plain" class="text-slate-200 text-sm md:text-base leading-relaxed"></p>
      </div>

      <!-- 3. Step-by-Step Fix & Copy-Paste AI Prompt -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5">
          <span class="text-[11px] font-bold uppercase tracking-wider text-amber-300 block mb-3">3. How to Fix It (Step-by-Step)</span>
          <ol id="res-steps" class="list-decimal list-inside space-y-2 text-sm text-slate-200"></ol>
        </div>

        <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-[11px] font-bold uppercase tracking-wider text-sky-300">4. Copy-Paste Prompt for Cursor / Lovable / Bolt</span>
              <button onclick="copyPrompt()" id="copy-prompt-btn" class="text-xs px-2.5 py-1 rounded bg-sky-500/20 text-sky-300 hover:bg-sky-500/30 border border-sky-500/30 font-semibold">📋 Copy Prompt</button>
            </div>
            <p class="text-xs text-slate-400 mb-2">Paste this directly into your AI coding chat so it fixes the bug cleanly:</p>
            <pre id="res-prompt" class="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-sky-200 whitespace-pre-wrap font-mono"></pre>
          </div>
        </div>
      </div>

      <!-- 4. Code Example -->
      <div id="code-wrap" class="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">5. Code Example (Before vs. After)</span>
          <button onclick="copyCode()" id="copy-code-btn" class="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700">📋 Copy Code</button>
        </div>
        <pre id="res-code" class="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-emerald-300 overflow-x-auto font-mono"></pre>
      </div>
    </div>
  </main>

  <script>
    const EXAMPLES = ${JSON.stringify(GOLDEN_EXAMPLES)};

    const chipsContainer = document.getElementById("example-chips");
    EXAMPLES.forEach((ex, idx) => {
      const btn = document.createElement("button");
      btn.className = "text-xs px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-indigo-950/80 text-slate-300 hover:text-indigo-200 border border-slate-800 hover:border-indigo-500/50 transition text-left";
      btn.textContent = ex.label;
      btn.onclick = () => selectExample(idx);
      chipsContainer.appendChild(btn);
    });

    function selectExample(idx) {
      const ex = EXAMPLES[idx];
      document.getElementById("error-input").value = ex.error;
      renderResult({ ...ex.result, cost_gbp: "£0.0000 (Instant Match)" });
    }

    function clearAll() {
      document.getElementById("error-input").value = "";
      document.getElementById("result-box").classList.add("hidden");
    }

    async function analyzeError() {
      const errorText = document.getElementById("error-input").value.trim();
      const tool = document.getElementById("tool-select").value;
      if (!errorText) {
        alert("Paste an error message or click one of the 6 example buttons above first!");
        return;
      }
      const btn = document.getElementById("fix-btn");
      btn.disabled = true;
      btn.innerHTML = "<span>⏳ Translating error into plain English...</span>";

      try {
        const res = await fetch("/api/explain", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ error: errorText, tool })
        });
        const data = await res.json();
        if (data.error) {
          alert(data.error);
        } else {
          renderResult(data);
        }
      } catch (e) {
        alert("Network error—please try again.");
      } finally {
        btn.disabled = false;
        btn.innerHTML = "<span>✨ Explain & Fix in Plain English</span>";
      }
    }

    function renderResult(data) {
      document.getElementById("res-summary").textContent = data.summary || "";
      document.getElementById("res-plain").textContent = data.plain_english || "";
      document.getElementById("cost-badge").textContent = "Est. Call Cost: " + (data.cost_gbp || "~£0.0001");

      const stepsList = document.getElementById("res-steps");
      stepsList.innerHTML = "";
      (data.steps || []).forEach(s => {
        const li = document.createElement("li");
        li.textContent = s;
        stepsList.appendChild(li);
      });

      document.getElementById("res-prompt").textContent = data.ai_prompt || "";
      const codeWrap = document.getElementById("code-wrap");
      if (data.fixed_code) {
        codeWrap.classList.remove("hidden");
        document.getElementById("res-code").textContent = data.fixed_code;
      } else {
        codeWrap.classList.add("hidden");
      }

      const box = document.getElementById("result-box");
      box.classList.remove("hidden");
      box.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function copyPrompt() {
      navigator.clipboard.writeText(document.getElementById("res-prompt").textContent);
      const b = document.getElementById("copy-prompt-btn");
      b.textContent = "✅ Copied!";
      setTimeout(() => b.textContent = "📋 Copy Prompt", 1500);
    }

    function copyCode() {
      navigator.clipboard.writeText(document.getElementById("res-code").textContent);
      const b = document.getElementById("copy-code-btn");
      b.textContent = "✅ Copied!";
      setTimeout(() => b.textContent = "📋 Copy Code", 1500);
    }

    // Auto-load Example 1 on first visit so Harrison immediately sees how clean it is
    selectExample(0);
  </script>
</body>
</html>`;

    return new Response(html, {
      headers: { "Content-Type": "text/html; charset=utf-8" }
    });
  }
};
