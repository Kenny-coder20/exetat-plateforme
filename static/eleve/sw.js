// Service worker : met en cache l'application élève pour un usage hors ligne.
const CACHE = 'exetat-eleve-v10';
const FICHIERS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith('/api/')) return; // l'API n'est jamais mise en cache : la banque vit dans localStorage
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => { const copie = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); return res; }).catch(() => caches.match('./index.html'))));
});
