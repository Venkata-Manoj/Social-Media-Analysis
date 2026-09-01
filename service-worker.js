/**
 * SocialPulse — Service Worker (PWA offline cache)
 * Cache-first for assets/data/html, network-first for /api/*
 * Gracefully degrades on file:// (SW only runs on http/https)
 * Version: v2 — bump CACHE_NAME to invalidate
 */

const CACHE_NAME = 'socialpulse-v2';
const PRECACHE_URLS = [
  './',
  './index.html',
  './site.webmanifest',
  './favicon.svg',
  // data — small json, cache-first ensures offline dashboard works
  './data/social_media_dataset.json',
  './data/dataset_stats.json',
  // assets — 8 figures
  './assets/fig1_sentiment.png',
  './assets/fig2_platform.png',
  './assets/fig3_timeline.png',
  './assets/fig4_scatter.png',
  './assets/fig5_hashtags.png',
  './assets/fig6_topic.png',
  './assets/fig7_hourly.png',
  './assets/fig8_usertype.png',
  // also support web/ scope when deployed from web/dist or web/public
  './web/manifest.json',
  './web/public/site.webmanifest',
  './web/public/icons/icon-192.png',
  './web/public/icons/icon-512.png',
  // when sw is at root, these are also precached via scope fallback
  'web/service-worker.js',
  'service-worker.js'
];

// Install — precache core assets
self.addEventListener('install', (event) => {
  // Skip waiting so new SW activates immediately (no need to close tabs)
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS.map((u) => {
        // Use no-cache to ensure fresh fetch during install, but tolerate failure for optional URLs
        return new Request(u, { cache: 'reload' });
      })).catch((err) => {
        // Precaching is best-effort — log but don't fail install if one asset 404 (e.g., CDN)
        console.warn('[SW] precache failed for some URLs (non-fatal):', err);
        // Try to cache what we can individually, ignoring failures
        return Promise.allSettled(
          PRECACHE_URLS.map((url) => caches.open(CACHE_NAME).then((c) => c.add(url).catch(()=>{})))
        );
      });
    })
  );
});

// Activate — clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle GET
  if (req.method !== 'GET') return;

  // Skip non-http(s) like chrome-extension, data:, blob:
  if (!url.protocol.startsWith('http')) return;

  // For SPA navigation (Accept: text/html), try network then cache fallback to index.html
  const isNavigation =
    req.mode === 'navigate' ||
    (req.headers.get('accept') && req.headers.get('accept').includes('text/html'));

  // --- API: network-first, fallback to cache (or offline JSON) ---
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          // Cache successful GETs for offline fallback (even though server says no-store, we cache for offline UX)
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone)).catch(()=>{});
          }
          return resp;
        })
        .catch(() =>
          caches.match(req).then((cached) => {
            if (cached) return cached;
            // Offline placeholder for API
            return new Response(
              JSON.stringify({ error: 'offline', offline: true, hint: 'Service worker: network unavailable, serving cached or offline fallback. File:// fallback still works for static dashboard.' }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json; charset=utf-8', 'X-SW-Cache': 'offline-fallback' }
              }
            );
          })
        )
    );
    return;
  }

  // --- Navigation: network-first with cache fallback to index.html ---
  if (isNavigation) {
    event.respondWith(
      fetch(req)
        .then((resp) => {
          if (resp.ok) {
            const clone = resp.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, clone)).catch(()=>{});
          }
          return resp;
        })
        .catch(() =>
          caches.match(req).then((cached) => cached || caches.match('./index.html') || caches.match('/index.html') || caches.match('index.html'))
        )
    );
    return;
  }

  // --- Assets / data / static: cache-first, stale-while-revalidate ---
  const isAsset = url.pathname.match(/\.(png|jpg|jpeg|svg|json|csv|js|css|webmanifest|woff2?|xml|txt)$/) !== null ||
                  url.pathname === '/' ||
                  url.pathname.endsWith('index.html');

  if (isAsset) {
    event.respondWith(
      caches.match(req).then((cached) => {
        if (cached) {
          // Stale-while-revalidate: update cache in background
          event.waitUntil(
            fetch(req)
              .then((netResp) => {
                if (netResp.ok) {
                  caches.open(CACHE_NAME).then((c) => c.put(req, netResp)).catch(()=>{});
                }
              })
              .catch(() => {})
          );
          return cached;
        }
        // Not in cache — network, then cache
        return fetch(req)
          .then((netResp) => {
            if (netResp.ok) {
              const clone = netResp.clone();
              caches.open(CACHE_NAME).then((c) => c.put(req, clone)).catch(()=>{});
            }
            return netResp;
          })
          .catch(() => {
            // If image fails, return offline placeholder? For now, just fail gracefully
            return cached;
          });
      })
    );
    return;
  }

  // --- Default: network-first with cache fallback ---
  event.respondWith(
    fetch(req)
      .then((resp) => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, clone)).catch(()=>{});
        }
        return resp;
      })
      .catch(() => caches.match(req))
  );
});

// Optional: listen for skipWaiting message from client
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
