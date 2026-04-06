const CACHE_VERSION = 'etude-line-v17';
const STATIC_CACHE = 'etude-line-static-v17';
const DYNAMIC_CACHE = 'etude-line-dynamic-v17';

const STATIC_ASSETS = [
  '/',
  '/login',
  '/static/offline.html',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/notification-sound.wav'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(names =>
      Promise.all(names.map(n => {
        if (n !== STATIC_CACHE && n !== DYNAMIC_CACHE) return caches.delete(n);
      }))
    ).then(() => self.clients.claim())
  );
});

// ============================================================
// FETCH — stratégies de cache
// ============================================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  if (request.method !== 'GET') return;

  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
  } else if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkOnly(request));
  } else if (url.pathname.startsWith('/dashboard/')) {
    event.respondWith(networkOnlyOfflineFallback(request));
  } else {
    event.respondWith(networkFirst(request));
  }
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const resp = await fetch(request);
    if (resp.ok) (await caches.open(STATIC_CACHE)).put(request, resp.clone());
    return resp;
  } catch { return new Response('Offline', { status: 503 }); }
}

async function networkFirst(request) {
  try {
    const resp = await fetch(request);
    if (resp.ok) (await caches.open(DYNAMIC_CACHE)).put(request, resp.clone());
    return resp;
  } catch {
    const cached = await caches.match(request);
    return cached || await caches.match('/static/offline.html') ||
      new Response('Offline', { status: 503 });
  }
}

async function networkOnly(request) {
  try { return await fetch(request); }
  catch {
    return new Response(JSON.stringify({ error: 'Connexion réseau requise' }), {
      status: 503, headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function networkOnlyOfflineFallback(request) {
  try { return await fetch(request); }
  catch {
    return await caches.match('/static/offline.html') ||
      new Response('Offline', { status: 503 });
  }
}

// ============================================================
// PUSH — notification système Android/Desktop hors application
// ============================================================
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) {}

  const title = data.title || '📚 Étude LINE';
  const ts = Date.now();

  const options = {
    body: data.body || 'Vous avez une nouvelle notification',
    icon: data.icon || '/static/icons/icon-192.png',
    badge: '/static/icons/icon-192.png',
    vibrate: [200, 100, 200],
    // Tag unique par notification → toutes s'empilent dans la barre Android
    tag: 'etudeline-' + ts,
    renotify: false,
    // requireInteraction: false = compatible tous navigateurs Android/iOS
    // La notification reste dans la barre système jusqu'à ce que l'utilisateur la ferme
    requireInteraction: false,
    silent: false,
    data: { url: data.url || '/', timestamp: ts }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
      .then(() => self.clients.matchAll({ type: 'window', includeUncontrolled: true }))
      .then(clientList => {
        clientList.forEach(c => c.postMessage({ type: 'PLAY_NOTIFICATION_SOUND' }));
      })
      .catch(err => console.error('[SW] showNotification error:', err))
  );
});

// ============================================================
// NOTIFICATION CLICK — ouvrir la bonne page
// ============================================================
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data && event.notification.data.url) || '/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(list => {
        for (const c of list) {
          if (c.url.includes(targetUrl) && 'focus' in c) return c.focus();
        }
        if (self.clients.openWindow) return self.clients.openWindow(targetUrl);
      })
  );
});

self.addEventListener('notificationclose', () => {});

// ============================================================
// MESSAGES depuis les pages (SHOW_NOTIFICATION, UPDATE_BADGE)
// ============================================================
self.addEventListener('message', (event) => {
  const msg = event.data;
  if (!msg) return;

  if (msg.type === 'SHOW_NOTIFICATION') {
    const { title, body, icon, url } = msg;
    const options = {
      body: body || 'Nouvelle notification',
      icon: icon || '/static/icons/icon-192.png',
      badge: '/static/icons/icon-192.png',
      vibrate: [300, 100, 300, 100, 600],
      tag: 'etudeline-push',
      renotify: true,
      requireInteraction: true,
      silent: false,
      data: { url: url || '/', timestamp: Date.now() }
    };
    event.waitUntil(
      self.registration.showNotification(title || '📚 Étude LINE', options)
        .then(() => self.clients.matchAll({ type: 'window', includeUncontrolled: true }))
        .then(list => list.forEach(c => c.postMessage({ type: 'PLAY_NOTIFICATION_SOUND' })))
    );
  }

  if (msg.type === 'UPDATE_BADGE') {
    const count = msg.count || 0;
    if ('setAppBadge' in self) {
      count > 0
        ? self.setAppBadge(count).catch(() => {})
        : self.clearAppBadge().catch(() => {});
    }
  }
});
