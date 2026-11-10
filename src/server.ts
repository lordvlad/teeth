import { join, normalize, sep } from "node:path";

const root = join(import.meta.dir, "..", "public");
const port = Number(process.env.PORT ?? 8791);

const server = Bun.serve({
  port,
  hostname: process.env.HOST ?? "0.0.0.0",
  async fetch(req) {
    if (req.method !== "GET" && req.method !== "HEAD") return new Response("Method Not Allowed", { status: 405 });
    let path = decodeURIComponent(new URL(req.url).pathname);
    if (path.endsWith("/")) path += "index.html";
    const full = normalize(join(root, path));
    if (full !== root && !full.startsWith(root + sep)) return new Response("Not Found", { status: 404 });
    const file = Bun.file(full);
    if (!(await file.exists())) return new Response("Not Found", { status: 404 });
    // sw.js and the HTML must revalidate so updates reach clients; the SW handles offline caching.
    const fresh = full.endsWith(".html") || full.endsWith("sw.js") || full.endsWith(".webmanifest");
    return new Response(file, { headers: { "Cache-Control": fresh ? "no-cache" : "public, max-age=3600" } });
  },
});

console.log(`teeth listening on http://${server.hostname}:${server.port}`);
