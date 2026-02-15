const CACHE_NAME = 'smarthome-v1';
const ASSETS = [
    './',
    './index.html',
    './dashboard.html',
    './style.css',
    './config.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});
