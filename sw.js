// Offline support for Friend di Frasi.
// Pages: network first (so new cards show up), falling back to the saved copy after 3s or offline.
// Fonts and icons: saved once, then served from the phone.
const CACHE = "frasi-v1";
const CORE = ["./", "./index.html", "./manifest.webmanifest",
  "./icons/icon-192.png", "./icons/icon-512.png", "./icons/maskable-512.png", "./icons/favicon-64.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  const key = req.mode === "navigate" ? "./index.html" : req;
  const net = fetch(req).then(res => { if (res.ok) cache.put(key, res.clone()); return res; });
  const saved = await cache.match(key, { ignoreSearch: true });
  if (!saved) return net;
  // Slow or no signal: show the saved copy; the network copy still refreshes the cache for next time.
  return Promise.race([net.catch(() => saved), new Promise(r => setTimeout(() => r(saved), 3000))]);
}

function cacheFirst(req) {
  return caches.open(CACHE).then(cache => cache.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok || res.type === "opaque") cache.put(req, res.clone());
    return res;
  })));
}

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(cacheFirst(req));
  } else if (url.origin === self.location.origin) {
    e.respondWith(url.pathname.includes("/icons/") ? cacheFirst(req) : networkFirst(req));
  }
});
