// Service Worker - AUTO UNINSTALL
// Ce service worker se désinstalle automatiquement pour corriger les erreurs de redirection

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    console.log('Deleting cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
        }).then(() => {
            console.log('Service Worker: All caches deleted');
            return self.registration.unregister();
        }).then(() => {
            console.log('Service Worker: Unregistered');
        })
    );
});

// Ne pas intercepter les requêtes - laisser passer
self.addEventListener('fetch', event => {
    return;
});
