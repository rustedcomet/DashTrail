import { build, files, version } from '$service-worker';

const CACHE_NAME = `speedometer-web-${version}`;
const APP_SHELL = [...build, ...files];

self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
	);
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) =>
			Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
		)
	);
});

self.addEventListener('fetch', (event) => {
	const request = event.request;
	const url = new URL(request.url);

	if (request.method !== 'GET' || url.pathname.startsWith('/api/')) {
		return;
	}

	event.respondWith(
		caches.match(request).then((cached) => cached ?? fetch(request))
	);
});
