import json
import sys
import time
import threading
import subprocess
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


WATCH_DIRS = [
    "content",
    "templates",
    "markdown_parser",
    "template_engine",
]

PORT = 8000

BUILD_VERSION = 0


def build():
    global BUILD_VERSION

    subprocess.run([sys.executable, "generate.py", "--dev"])

    BUILD_VERSION += 1


class Handler(FileSystemEventHandler):
    last_build = 0

    def on_modified(self, event):
        if event.is_directory:
            return

        if "__pycache__" in event.src_path:
            return

        now = time.time()

        if now - self.last_build < 0.3:
            return

        self.last_build = now

        print(f"Changed: {event.src_path}")

        build()


class DevHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/version":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(
                json.dumps({"version": BUILD_VERSION}).encode()
            )
            return

        super().do_GET()


def serve():
    handler = partial(DevHandler, directory="public")

    server = ThreadingHTTPServer(
        ("localhost", PORT),
        handler,
    )

    print(f"http://localhost:{PORT}")

    server.serve_forever()


def main():
    build()

    threading.Thread(target=serve, daemon=True).start()

    observer = Observer()

    handler = Handler()

    for directory in WATCH_DIRS:
        observer.schedule(handler, directory, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()