// MechanicProof Service Worker v1.0
const CACHE_NAME = 'mechanicproof-v1';
const STATIC_ASSETS = [
  '/',
  '/manifest.json'
];

// API routes that should NOT be cached
const NO_CACHE_PATTERNS = [
  '/api/',
  '/search',
  '/lookup'
];

// ─── Install: pre-cache static assets ───────────────────────────────────────
self.addEventListener('install', event => {
  console.log('[SW] Installing MechanicProof Service Worker');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Pre-cache failed (ok in dev):', err);
      });
    }).then(() => self.skipWaiting())
  );
});

// ─── Activate: clean up old caches ──────────────────────────────────────────
self.addEventListener('activate', event => {
  console.log('[SW] Activating MechanicProof Service Worker');
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => {
          console.log('[SW] Deleting old cache:', k);
          return caches.delete(k);
        })
      )
    ).then(() => self.clients.claim())
  );
});

// ─── Fetch: network-first for API, cache-first for static ───────────────────
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  const isApiCall = NO_CACHE_PATTERNS.some(p => url.pathname.startsWith(p));
  const isGetRequest = event.request.method === 'GET';

  if (!isGetRequest || isApiCall) {
    // For API calls and non-GET: network only, no cache
    event.respondWith(
      fetch(event.request).catch(() => {
        if (isApiCall) {
          return new Response(
            JSON.stringify({ error: 'offline', message: 'No internet connection. Please check your connection and try again.' }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
          );
        }
        return new Response('Offline', { status: 503 });
      })
    );
    return;
  }

  // For static assets: cache-first with network fallback
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      if (cachedResponse) {
        // Serve from cache, also update cache in background
        fetch(event.request).then(networkResponse => {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, networkResponse.clone());
            });
          }
        }).catch(() => {});
        return cachedResponse;
      }

      // Not in cache: fetch from network and cache it
      return fetch(event.request).then(networkResponse => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type === 'opaque') {
          return networkResponse;
        }
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseToCache);
        });
        return networkResponse;
      }).catch(() => {
        // Offline fallback for the main page
        if (url.pathname === '/' || url.pathname === '/index.html') {
          return caches.match('/');
        }
        return new Response('Resource not available offline', { status: 503 });
      });
    })
  );
});

// ─── Push notifications (for future recall alerts) ──────────────────────────
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'MechanicProof';
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/manifest.json',
    badge: '/manifest.json',
    data: data.url || '/',
    vibrate: [200, 100, 200],
    actions: data.actions || []
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data || '/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) return client.focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});

// ─── Background sync (future: sync service records when back online) ─────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-service-records') {
    event.waitUntil(syncServiceRecords());
  }
});

async function syncServiceRecords() {
  try {
    const db = await openIndexedDB();
    const pendingRecords = await db.getAll('pending_sync');
    for (const record of pendingRecords) {
      await fetch('/api/garage/records', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(record)
      });
    }
    console.log('[SW] Synced', pendingRecords.length, 'records');
  } catch (err) {
    console.warn('[SW] Sync failed:', err);
  }
}

function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('mechanicproof', 1);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
    req.onupgradeneeded = e => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('pending_sync')) {
        db.createObjectStore('pending_sync', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

console.log('[SW] MechanicProof Service Worker v1.0 loaded');
