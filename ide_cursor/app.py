import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


QUESTIONS = [
    {"id": 1, "text": "Какие школьные предметы вам даются легче всего?"},
    {"id": 2, "text": "В какой рабочей среде вы чувствуете себя комфортнее всего?"},
    {"id": 3, "text": "Что мотивирует вас учиться новому больше всего?"},
    {"id": 4, "text": "Какие навыки вы хотели бы развивать в первую очередь?"},
    {"id": 5, "text": "Какие задачи приносят вам больше удовлетворения — аналитические или творческие?"},
]

# Хранилище ответов в памяти
ANSWERS = []

ROOT = Path(__file__).parent.resolve()
INDEX_FILE = ROOT / "index.html"


class SurveyHandler(BaseHTTPRequestHandler):
    server_version = "SurveyServer/0.1"

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/" or self.path == "/index.html":
            if not INDEX_FILE.exists():
                self._set_headers(500)
                self.wfile.write(b"index.html not found")
                return
            content = INDEX_FILE.read_bytes()
            self._set_headers(content_type="text/html; charset=utf-8")
            self.wfile.write(content)
            return

        if self.path == "/questions":
            self._set_headers()
            body = json.dumps({"questions": QUESTIONS}, ensure_ascii=False).encode("utf-8")
            self.wfile.write(body)
            return

        self._set_headers(404)
        self.wfile.write(b'{"error": "not found"}')

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/answers":
            self._set_headers(404)
            self.wfile.write(b'{"error": "not found"}')
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(b'{"error": "invalid json"}')
            return

        ANSWERS.append(payload)

        self._set_headers(201)
        self.wfile.write(b'{"status": "ok"}')

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        # Перенаправляем логи в stdout без адресов клиента
        message = "%s - %s" % (self.log_date_time_string(), format % args)
        print(message)


def run_server() -> None:
    host, port = "0.0.0.0", 8000
    httpd = HTTPServer((host, port), SurveyHandler)
    print(f"Server running on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()

