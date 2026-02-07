const CACHE_NAME = 's-quiz-v3';
const ASSETS = [
    '/',
    '/manifest.json',
    '/static/script.js',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    // Network-First strategy for the root and API calls
    event.respondWith(
        fetch(event.request)
            .catch(() => caches.match(event.request))
    );
});
