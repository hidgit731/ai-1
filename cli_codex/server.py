import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import List, Dict

QUESTIONS: List[Dict[str, str]] = [
    {"id": 1, "text": "Какие школьные предметы приносят вам больше всего удовольствия?"},
    {"id": 2, "text": "Есть ли у вас любимое хобби, которое хотелось бы превратить в профессию?"},
    {"id": 3, "text": "Предпочитаете работать с людьми, цифрами или технологиями?"},
    {"id": 4, "text": "В какой рабочей среде вы чувствуете себя наиболее продуктивно?"},
    {"id": 5, "text": "Что для вас важнее в профессии: стабильность или разнообразие задач?"},
]

ANSWERS: List[Dict[str, str]] = []

STATIC_DIR = Path(__file__).parent / "static"


class QuestionnaireHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # type: ignore[override]
        if self.path == "/questions":
            self._send_json(QUESTIONS)
            return

        if self.path in {"/", "/index.html"}:
            self._serve_static("index.html", "text/html; charset=utf-8")
            return

        self.send_error(404, "Not Found")

    def do_POST(self) -> None:  # type: ignore[override]
        if self.path != "/answers":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if isinstance(payload, dict):
            ANSWERS.append(payload)
            self._send_json({"status": "accepted"}, status=201)
        else:
            self.send_error(400, "Payload must be an object")

    def log_message(self, format: str, *args: str) -> None:  # type: ignore[override]
        # Reduce noise in the console logs.
        return

    def _serve_static(self, filename: str, content_type: str) -> None:
        file_path = STATIC_DIR / filename
        if not file_path.exists():
            self.send_error(404, "File not found")
            return

        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer((host, port), QuestionnaireHandler)
    print(f"Server running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
