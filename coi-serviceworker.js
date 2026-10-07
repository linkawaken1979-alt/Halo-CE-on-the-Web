/*
 * HARRYAMA GAMES - Halo CE COI Service Worker
 * Multi-tab safe
 */

const VERSION = "halo-coi-v3";

self.addEventListener("install", () => {
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    event.waitUntil(self.clients.claim());
});

function isWebSocket(request) {
    const upgrade = request.headers.get("Upgrade");

    return (
        request.url.startsWith("ws://") ||
        request.url.startsWith("wss://") ||
        (upgrade && upgrade.toLowerCase() === "websocket")
    );
}

function isHttp(request) {
    return (
        request.url.startsWith("http://") ||
        request.url.startsWith("https://")
    );
}

self.addEventListener("fetch", event => {
    const request = event.request;

    /*
     * Never intercept WebSockets.
     */
    if (isWebSocket(request)) {
        return;
    }

    /*
     * Only handle HTTP/HTTPS.
     */
    if (!isHttp(request)) {
        return;
    }

    /*
     * Only modify GET requests.
     */
    if (request.method !== "GET") {
        return;
    }

    event.respondWith(
        (async () => {
            try {
                const response = await fetch(request);

                /*
                 * If the browser/network already failed,
                 * don't attempt to rebuild the response.
                 */
                if (!response || !response.ok && response.type !== "opaque") {
                    return response;
                }

                const headers = new Headers(response.headers);

                headers.set(
                    "Cross-Origin-Opener-Policy",
                    "same-origin"
                );

                headers.set(
                    "Cross-Origin-Embedder-Policy",
                    "require-corp"
                );

                return new Response(response.body, {
                    status: response.status,
                    statusText: response.statusText,
                    headers: headers
                });

            } catch (error) {
                /*
                 * Let the original network error propagate.
                 * NEVER create Response(... status: 0).
                 */
                console.warn(
                    "[COI] Network request failed:",
                    request.url,
                    error
                );

                throw error;
            }
        })()
    );
});