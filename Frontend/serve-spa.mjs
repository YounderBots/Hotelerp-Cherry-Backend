#!/usr/bin/env node
/**
 * Static host for the built SPA, with a history fallback that only applies to
 * navigations.
 *
 * WHY THIS EXISTS
 *   The deployment at 168.231.103.18:5700 answers `200 text/html` -- the SPA's
 *   index.html -- for EVERY unmatched path, including
 *   `/does-not-exist-xyz.jpg` and `/templates/static/upload_image/x.png`. The
 *   rewrite is unconditional, so:
 *
 *     * a genuinely missing asset returns 200 HTML, and anything checking for
 *       404s sees a success;
 *     * a broken <img> or <script> src cannot be distinguished from a working
 *       one at the HTTP layer;
 *     * an earlier QA pass read the missing-uploads finding (LIVE-002) the
 *       wrong way round for exactly this reason -- it took a 200 on an image
 *       path as evidence that the gateway was serving it, when 200 there is
 *       never evidence of anything.
 *
 *   A single-page app genuinely does need index.html for unknown paths, because
 *   React Router resolves them in the browser. The fix is not to drop the
 *   fallback, it is to make it mean what it says: a client-side ROUTE has no
 *   file extension and asks for HTML; an ASSET has an extension and either
 *   exists or is a 404.
 *
 * USAGE
 *   node serve-spa.mjs                     # serve ./dist on :5700
 *   node serve-spa.mjs --dir build --port 8080
 *
 * No dependencies. The only thing it needs is a completed `npm run build`.
 */

import { createServer } from "node:http";
import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { extname, join, normalize, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));

// ---------------------------------------------------------------------------
// Should this path fall back to index.html?
// ---------------------------------------------------------------------------

/**
 * Extensions a browser requests as a sub-resource or navigates to directly.
 * A request for one of these that does not exist on disk is a 404, full stop --
 * serving HTML for it is what turns a missing image into a silent success.
 */
const ASSET_EXTENSIONS = new Set([
  // the ones a SPA build actually emits
  ".js", ".mjs", ".css", ".map", ".json", ".txt", ".xml",
  // media and fonts
  ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico", ".bmp",
  ".mp4", ".webm", ".ogg", ".mp3", ".wav", ".flac", ".aac",
  ".woff", ".woff2", ".ttf", ".otf", ".eot",
  // documents and archives: a user pasting one into the address bar wants the
  // file or a 404, never the SPA shell
  ".pdf", ".zip", ".gz", ".csv", ".xlsx", ".docx", ".xls", ".doc",
  // uploads this app serves
  ".jpg", ".jpeg", ".png", ".gif", ".webp",
]);

/**
 * True when `pathname` should be answered with index.html rather than a 404.
 *
 * Three conditions, all necessary:
 *   1. no file extension -- a client-side route like /room_view, not a file;
 *   2. the client asked for HTML -- `Accept: text/html`, which is what a
 *      navigation sends and what fetch()/XHR for an asset does not;
 *   3. it is not a well-known static path prefix.
 *
 * (2) is the important one and it is what makes the behaviour correct without
 * having to guess from extensions alone: a `<script src>` or `<img src>` never
 * sends `Accept: text/html`, so it can never be handed the shell.
 */
export function isClientRoute(pathname, acceptHeader) {
  const ext = extname(pathname).toLowerCase();
  if (ext) return false;                                  // (1)
  if (ASSET_EXTENSIONS.has(ext)) return false;            // (1), belt and braces
  const acceptsHtml = String(acceptHeader || "")
    .toLowerCase()
    .split(",")
    .some((part) => part.trim().startsWith("text/html"));
  if (!acceptsHtml) return false;                          // (2)
  if (STATIC_PREFIXES.some((p) => pathname.startsWith(p))) return false;  // (3)
  return true;
}

/** Paths that are always assets, whatever they look like. */
const STATIC_PREFIXES = ["/assets/", "/static/", "/templates/"];

// ---------------------------------------------------------------------------
// Path safety
// ---------------------------------------------------------------------------

/**
 * Resolve a URL path to a file inside `root`, or null if it escapes or is an
 * escape attempt.
 *
 * A `..` segment is refused outright rather than normalised away. Normalising
 * would be safe -- nothing outside `root` can be reached either way, because
 * the result is checked against the root prefix -- but it would answer an
 * attempt to climb out with `200` and the SPA shell, which hides the attempt
 * and reads as success. No client-side route contains `..`, so refusing costs
 * nothing.
 *
 * `%2e%2e` decodes to `..` before the segment check, so encoded traversal is
 * caught by the same rule.
 */
export function resolveWithin(root, pathname) {
  let decoded;
  try {
    decoded = decodeURIComponent(pathname);
  } catch {
    return null;                                   // malformed percent-encoding
  }
  if (decoded.includes("\0")) return null;

  const segments = decoded.split(/[/\\]/);
  if (segments.some((s) => s === "..")) return null;

  const clean = normalize(decoded).replace(/^([/\\])+/, "");
  const full = resolve(root, clean);
  const rootFull = resolve(root);
  if (full !== rootFull && !full.startsWith(rootFull + sep)) return null;
  return full;
}

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------

const CONTENT_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".otf": "font/otf",
  ".map": "application/json; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".pdf": "application/pdf",
  ".webm": "video/webm",
  ".mp4": "video/mp4",
};

const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  // index.html must never be cached, or a deploy leaves stale asset references
  // in clients for as long as the cache entry lives.
  "Cache-Control": "no-cache",
};

function send(res, status, body, headers = {}) {
  res.writeHead(status, { ...SECURITY_HEADERS, ...headers });
  res.end(body);
}

async function tryFile(res, filePath, method) {
  let info;
  try {
    info = await stat(filePath);
  } catch {
    return false;
  }
  if (!info.isFile()) return false;
  const ext = extname(filePath).toLowerCase();
  const type = CONTENT_TYPES[ext] || "application/octet-stream";
  // Hashed build assets are immutable; everything else must revalidate.
  const cacheable = filePath.includes(`${sep}assets${sep}`);
  res.writeHead(200, {
    ...SECURITY_HEADERS,
    "Content-Type": type,
    "Content-Length": info.size,
    "Cache-Control": cacheable
      ? "public, max-age=31536000, immutable"
      : "no-cache",
  });
  if (method === "HEAD") {
    res.end();
    return true;
  }
  createReadStream(filePath).pipe(res);
  return true;
}

/**
 * The request target's path, WITHOUT the WHATWG URL parser's normalisation.
 *
 * `new URL(req.url, base)` resolves `..` segments before this code ever sees
 * them, so `/../Backend/Services` arrives as `/Backend/Services` and a traversal
 * attempt is indistinguishable from an ordinary unknown route. Splitting the
 * target by hand keeps the bytes the client actually sent, which is what the
 * `..` check in resolveWithin() needs.
 */
export function rawPathname(requestTarget) {
  let target = String(requestTarget || "/");
  const hash = target.indexOf("#");
  if (hash !== -1) target = target.slice(0, hash);
  const query = target.indexOf("?");
  if (query !== -1) target = target.slice(0, query);
  return target || "/";
}

export function createSpaServer({ dir }) {
  const root = resolve(dir);
  return createServer(async (req, res) => {
    const method = (req.method || "GET").toUpperCase();
    const pathname = rawPathname(req.url);

    if (method !== "GET" && method !== "HEAD") {
      return send(res, 405, "Method Not Allowed", { Allow: "GET, HEAD" });
    }

    const filePath = resolveWithin(root, pathname);
    if (filePath === null) {
      return send(res, 400, "Bad Request");
    }

    // A directory request that exists: serve its index if there is one.
    try {
      const info = await stat(filePath);
      if (info.isDirectory()) {
        const index = join(filePath, "index.html");
        if (await tryFile(res, index, method)) return;
        return send(res, 403, "Forbidden");
      }
    } catch {
      /* fall through to the fallback logic */
    }

    if (await tryFile(res, filePath, method)) return;

    // Not a file. A client-side ROUTE gets the SPA shell; anything else is a
    // genuine 404, and saying so is the entire point of this server.
    if (isClientRoute(pathname, req.headers.accept)) {
      if (await tryFile(res, join(root, "index.html"), method)) return;
    }

    send(res, 404, "Not Found", { "Content-Type": "text/plain; charset=utf-8" });
  });
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const out = { dir: join(HERE, "dist"), port: 5700, host: "127.0.0.1" };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--dir") out.dir = resolve(argv[++i]);
    else if (argv[i] === "--port") out.port = Number(argv[++i]);
    else if (argv[i] === "--host") out.host = argv[++i];
  }
  return out;
}

const isMain = process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url));
if (isMain) {
  const { dir, port, host } = parseArgs(process.argv.slice(2));
  const root = resolve(dir);
  stat(join(root, "index.html"))
    .then(() => {
      const server = createSpaServer({ dir: root });
      server.listen(port, host, () => {
        console.log(`serving ${root}`);
        console.log(`  http://${host}:${port}`);
        console.log("  history fallback: client-side routes only (Accept: text/html)");
      });
    })
    .catch(() => {
      console.error(`no index.html in ${root} -- run "npm run build" first`);
      process.exit(1);
    });
}