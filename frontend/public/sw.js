/**
 * Service Worker – Studienkolleg Aachen PWA
 * Strategie:
 *  - Statische Assets (JS/CSS/Fonts): Cache-First mit Offline-Fallback
 *  - HTML-Navigationen: Network-First mit Fallback auf Offline-Shell
 *  - API-Requests: NIEMALS cachen (Auth + CSRF-sensitive)
 */
const CACHE_VERSION = 'stk-aachen-v1.5.0';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const RUNTIME_CACHE = `${CACHE_VERSION}-runtime`;

const CORE_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
  '/apple-touch-icon.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => !k.startsWith(CACHE_VERSION)).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // NEVER cache API calls
  if (url.pathname.startsWith('/api/')) return;

  // Only handle GET
  if (request.method !== 'GET') return;

  // HTML navigation: Network-First
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((resp) => {
          const clone = resp.clone();
          caches.open(RUNTIME_CACHE).then((c) => c.put(request, clone)).catch(() => {});
          return resp;
        })
        .catch(() => caches.match(request).then((c) => c || caches.match('/')))
    );
    return;
  }

  // Static assets: Cache-First
  if (['style', 'script', 'font', 'image'].includes(request.destination)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((resp) => {
          if (resp && resp.status === 200 && resp.type === 'basic') {
            const clone = resp.clone();
            caches.open(RUNTIME_CACHE).then((c) => c.put(request, clone)).catch(() => {});
          }
          return resp;
        }).catch(() => cached);
      })
    );
  }
});

// Skip-Waiting Trigger von der App
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
