import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

HOST = "127.0.0.1"
PORT = 8000
ROOT = Path(__file__).parent

HTML = (ROOT / "assistant_ui.html").read_text(encoding="utf-8")


def get_gemini_api_key():
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )

TASKS = {
    "grade": [sys.executable, "grade.py"],
    "tests": [sys.executable, "-m", "pytest", "tests", "-q"],
    "part1": [sys.executable, "-m", "pytest", "tests/test_part1.py", "-q"],
    "part2": [sys.executable, "-m", "pytest", "tests/test_part2.py", "-q"],
    "part3": [sys.executable, "-m", "pytest", "tests/test_part3.py", "-q"],
    "part4": [sys.executable, "-m", "pytest", "tests/test_part4.py", "-q"],
}


class AssistantHandler(BaseHTTPRequestHandler):
    def _send(self, status, content_type, body):
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body_bytes)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", HTML)
            return
        self._send(404, "text/plain; charset=utf-8", "Not found")

    def do_POST(self):
        if self.path not in ("/api/chat", "/api/run", "/api/compare"):
            self._send(404, "application/json; charset=utf-8", '{"error":"Not found"}')
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            if self.path == "/api/compare":
                api_key = get_gemini_api_key()
                if not api_key:
                    raise RuntimeError(
                        "Thiếu GEMINI_API_KEY. Hãy đặt Gemini key rồi khởi động lại assistant_ui.py."
                    )
                os.environ["OPENAI_API_KEY"] = api_key
                from template import compare_models

                result = compare_models(
                    payload.get("prompt", "Explain artificial intelligence in one sentence.")
                )
                self._send(
                    200,
                    "application/json; charset=utf-8",
                    json.dumps(
                        {
                            "main_model": os.getenv("LAB_MODEL", "gemini-3.8-flash"),
                            "mini_model": os.getenv("LAB_MINI_MODEL", "gemini-3.5-flash-lite"),
                            "main_response": result["gpt4o_response"],
                            "mini_response": result["mini_response"],
                            "main_latency": result["gpt4o_latency"],
                            "mini_latency": result["mini_latency"],
                            "main_cost": result["gpt4o_cost_estimate"],
                        },
                        ensure_ascii=False,
                    ),
                )
                return

            if self.path == "/api/run":
                task = payload.get("task")
                command = TASKS.get(task)
                if command is None:
                    raise ValueError("Unknown task")
                command_environment = os.environ.copy()
                command_environment["PYTHONIOENCODING"] = "utf-8"
                command_environment["PYTHONUTF8"] = "1"
                result = subprocess.run(
                    command,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=command_environment,
                    timeout=120,
                )
                self._send(
                    200,
                    "application/json; charset=utf-8",
                    json.dumps(
                        {"ok": result.returncode == 0, "output": (result.stdout + result.stderr).strip()},
                        ensure_ascii=False,
                    ),
                )
                return

            model = payload.get("model")
            messages = payload.get("messages", [])
            if not model or not messages:
                raise ValueError("model and messages are required")
            api_key = get_gemini_api_key()
            if not api_key:
                raise RuntimeError(
                    "Thiếu GEMINI_API_KEY. Hãy đặt Gemini key trong .env hoặc PowerShell "
                    "rồi khởi động lại assistant_ui.py."
                )

            from openai import OpenAI

            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENAI_BASE_URL") or None,
            )
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=512,
            )
            content = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)
            self._send(
                200,
                "application/json; charset=utf-8",
                json.dumps(
                    {
                        "content": content,
                        "usage": {
                            "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                            "completion_tokens": getattr(usage, "completion_tokens", 0),
                        },
                    },
                    ensure_ascii=False,
                ),
            )
        except Exception as error:
            self._send(
                500,
                "application/json; charset=utf-8",
                json.dumps({"error": str(error)}, ensure_ascii=False),
            )

    def log_message(self, format_string, *args):
        print(f"[{self.log_date_time_string}] {format_string % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), AssistantHandler)
    print(f"Assistant UI: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping assistant UI.")
    finally:
        server.server_close()
