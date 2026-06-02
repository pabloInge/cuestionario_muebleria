import http.server
import json
import urllib.request
import urllib.parse
import os

PORT = 8080


def send_via_formsubmit(to, subject, text):
    """Send via FormSubmit API (server-side, no CORS issues)."""
    data = json.dumps({
        "_captcha": "false",
        "_subject": subject,
        "relevamiento": text
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Origin": "http://localhost:8080",
        "Referer": "http://localhost:8080/",
    }

    req = urllib.request.Request(
        f"https://formsubmit.co/ajax/{to}",
        data=data,
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/send":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                to = body.get("_to", "projectumsoft@gmail.com")
                subject = body.get("_subject", "Relevamiento de Requerimientos")
                text = body.get("relevamiento", "")

                result = send_via_formsubmit(to, subject, text)
                ok = result.get("success") and result.get("success") != "false"
                self._json(200, {"success": True, "delivered": ok, "message": "Enviado correctamente" if ok else "No se pudo enviar desde servidor. Reintentando desde navegador..."})
            except Exception as e:
                self._json(200, {"success": True, "delivered": False, "message": f"Fallo servidor: {e}. Reintentando desde navegador..."})
        else:
            self._json(404, {"error": "Not found"})

    def do_GET(self):
        super().do_GET()

    def _json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[SERVER] {args[0]} {args[1]} {args[2]}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"\n  Servidor: http://localhost:{PORT}")
    print(f"  Ctrl+C para detener\n")
    httpd = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Detenido.")
