import json
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 8000
REMOTE = "https://halo-web-signaling.otherness-bugs.workers.dev"

class Handler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/presence":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)

            url = REMOTE + "/v1/presence"

            request = urllib.request.Request(
                url,
                data=body,
                method="POST",
                headers={
                    "Content-Type": self.headers.get(
                        "Content-Type",
                        "application/json"
                    ),
                    "Accept": self.headers.get(
                        "Accept",
                        "application/json"
                    ),
                },
            )

            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    data = response.read()

                    self.send_response(response.status)
                    self.send_header(
                        "Content-Type",
                        response.headers.get(
                            "Content-Type",
                            "application/json"
                        )
                    )
                    self.send_header(
                        "Access-Control-Allow-Origin",
                        "*"
                    )
                    self.end_headers()
                    self.wfile.write(data)

            except urllib.error.HTTPError as e:
                data = e.read()

                self.send_response(e.code)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )
                self.end_headers()
                self.wfile.write(data)

            except Exception as e:
                data = json.dumps({
                    "error": str(e)
                }).encode()

                self.send_response(502)
                self.send_header(
                    "Content-Type",
                    "application/json"
                )
                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*"
                )
                self.end_headers()
                self.wfile.write(data)

            return

        self.send_error(404)

server = ThreadingHTTPServer(("localhost", PORT), Handler)

print()
print("========================================")
print(" Halo CE local server")
print("========================================")
print(f" Game:   http://localhost:{PORT}")
print(f" Proxy:  http://localhost:{PORT}/api/presence")
print("========================================")
print(" Press Ctrl+C to stop")
print()

try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
    server.server_close()