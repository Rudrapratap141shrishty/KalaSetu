/**
 * KalaSetu Mobile Application Service Worker
 * Handles offline asset caching, network-first strategy, and background sync.
 */

const CACHE_NAME = 'kalasetu-artisan-v1.0.0';
const STATIC_ASSETS = [
  '/',
  '/static/css/design_system.css',
  '/static/css/mobile_app.css',
  '/static/css/scanner.css',
  '/static/css/payment_modal.css',
  '/static/css/delivery_map.css',
  '/static/js/api_client.js',
  '/static/js/auth_service.js',
  '/static/js/ai_scanner.js',
  '/static/js/marketplace.js',
  '/static/js/payment_gateway.js',
  '/static/js/delivery_tracker.js',
  '/static/js/app.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Pre-caching offline static assets');
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing obsolete cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network first with cache fallback for HTML and API, cache-first for static CSS/JS
  if (event.request.url.includes('/api/') || event.request.url.includes('/graphql')) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  } else {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request);
      })
    );
  }
});
