import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, abort

BASE_DIR = Path(__file__).resolve().parent

# Serve files from project root so index.html and assets/ are reachable
app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="")

ALLOWED_PREFIXES = ("assets/", "readme-images/", "favicon.svg", "index.html")


@app.route("/")
def index():
    """Serve the main index.html"""
    return send_from_directory(str(BASE_DIR), "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/<path:filepath>")
def static_files(filepath):
    """Serve static files (assets, images, css, js, etc)."""
    # Basic security: only serve files under allowed prefixes
    if not any(filepath.startswith(p) for p in ALLOWED_PREFIXES):
        # allow direct requests for top-level files like README.md if needed
        allowed_top = ("README.md", "style-guide.md")
        if filepath not in allowed_top:
            abort(404)

    target = BASE_DIR / filepath
    if not target.exists() or not target.is_file():
        abort(404)

    return send_from_directory(str(BASE_DIR), filepath)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Use 0.0.0.0 so it's reachable from other devices on your network if needed
    app.run(host="0.0.0.0", port=port, debug=True)
