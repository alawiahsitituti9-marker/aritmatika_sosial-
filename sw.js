/* Service worker UntungCerdas.
 * Membuat aplikasi bisa diinstal dan tetap berjalan offline setelah dibuka sekali.
 * - File aplikasi (HTML, kode Python, ikon): network-first, sehingga pembaruan dari
 *   GitHub langsung terpakai saat online, dan salinan cache dipakai saat offline.
 * - Pyodide (Python di browser) dari CDN: cache-first, karena versinya tetap.
 * - Permintaan AI (POST ke Google Gemini) tidak disentuh dan selalu butuh internet.
 */
const VERSI = "untungcerdas-v1";
const CACHE_APP = VERSI + "-app";
const CACHE_PYODIDE = "untungcerdas-pyodide-0.26.4";
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/";

const FILE_APP = [
  "./", "index.html", "manifest.webmanifest",
  "soal.py", "permainan.py", "materi.py", "rmt.py", "ai_tutor.py", "web_api.py",
  "ikon/ikon-192.png", "ikon/ikon-512.png", "ikon/ikon-maskable-512.png", "ikon/apple-touch-icon.png",
];
const FILE_PYODIDE = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"];

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const app = await caches.open(CACHE_APP);
    await app.addAll(FILE_APP);
    // Pyodide disimpan sebisanya; jika gagal, akan tersimpan saat pertama kali dimuat.
    const py = await caches.open(CACHE_PYODIDE);
    await Promise.all(FILE_PYODIDE.map(f => py.add(PYODIDE + f).catch(() => null)));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    for (const nama of await caches.keys()) {
      if (nama !== CACHE_APP && nama !== CACHE_PYODIDE) await caches.delete(nama);
    }
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;               // permintaan AI (POST) tidak di-cache
  const url = new URL(req.url);

  if (url.href.startsWith(PYODIDE)) {             // Pyodide: cache-first
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_PYODIDE);
      const ada = await cache.match(req);
      if (ada) return ada;
      const resp = await fetch(req);
      if (resp.ok) cache.put(req, resp.clone());
      return resp;
    })());
    return;
  }

  if (url.origin === self.location.origin) {      // file aplikasi: network-first
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_APP);
      try {
        const resp = await fetch(req);
        if (resp.ok) cache.put(req, resp.clone());
        return resp;
      } catch (e) {
        const ada = await cache.match(req, { ignoreSearch: true });
        if (ada) return ada;
        if (req.mode === "navigate") return cache.match("index.html");
        throw e;
      }
    })());
  }
});
