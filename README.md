# Foodie — Static website served with a small Flask app

An offline/locally-hostable static website ("Foodie") with assets (HTML, CSS, JS, images) and a tiny Flask wrapper that serves the files. The project is intended to be run locally for development or packaged into a Docker image for simple deployment.

This README documents the project layout, how the Flask server serves files, how to run and build the Docker image, and useful development notes.

## Quick summary

- Language / runtime: Python 3 (Flask)
- Purpose: Serve a static restaurant/food landing site (index.html + assets)
- Main entry: `app.py` (Flask app that serves `index.html` and files under `assets/`)
- Web server port: 5000 (default, changeable via `PORT` environment variable)

## Project structure

Top-level files and folders (important ones):

- `app.py` — Flask application used to serve `index.html` and static files.
- `Dockerfile` — Docker image definition to run the app in a container.
- `requirements.txt` — Python dependencies (Flask).
- `index.html` — Main static HTML page (the site).
- `index.txt` — Plain text copy / notes extracted from the HTML.
- `README.md` — (this file)
- `style-guide.md` — notes and style constants used in the project.
- `favicon.svg` — site favicon.
- `readme-images/` — example screenshot(s) used in docs.
- `assets/` — all static web assets:
  - `assets/css/style.css` — main stylesheet.
  - `assets/js/script.js` — site behavior (menu toggle, search, scroll interactions).
  - `assets/images/` — all images used by the site (hero, banners, menu images, icons, etc.)

Example of how files are used:

- Browser request `/` -> served with `index.html`.
- Browser requests `/assets/js/script.js` -> served by the Flask static route.

## How the app works (internals)

The small Flask app in `app.py` is a lightweight static file server with three routes:

- `/` — returns `index.html` using Flask's `send_from_directory`.
- `/health` — a simple JSON health check: `{ "status": "ok" }`.
- `/<path:filepath>` — serves static files from the repository root but only when the requested path starts with an allowed prefix. This is a basic safety mechanism to avoid serving arbitrary files from the filesystem.

Key implementation details (see `app.py`):

- `static_folder` for the Flask app is set to the project root so relative paths like `assets/css/style.css` match correctly.
- `ALLOWED_PREFIXES = ("assets/", "readme-images/", "favicon.svg", "index.html")` — requests are validated against these prefixes. Top-level allowed files also include `README.md` and `style-guide.md` when explicitly requested by the route.
- If a requested file does not exist or is not permitted, the app returns HTTP 404.

This setup is intentionally minimal and intended for local/dev usage. For production you should serve static files via a proper web server (Nginx, CDN) and not through Flask in debug mode.

## Prerequisites

- Python 3.8+ installed and available as `python` (or `python3`).
- (Optional) Docker if you want to run the app in a container.

## Run locally (PowerShell instructions)

1. Open a PowerShell prompt in the project root (`Application-2.0`).

2. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
# Activate the venv in PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies and run the app:

```powershell
pip install -r requirements.txt
python app.py
```

4. Open a browser and navigate to:

- http://localhost:5000/ — the site
- http://localhost:5000/health — health JSON endpoint

Notes:

- The server defaults to debug mode as configured in `app.py`. For production, set `debug=False` and use a production WSGI server (Gunicorn, uWSGI) or a proper static-file server.
- To change the port, set the `PORT` environment variable before running:

```powershell
$env:PORT = '8080'
python app.py
```

## Run with Docker

Build the Docker image (from project root):

```powershell
docker build -t foodie:latest .
```

Run the container and forward port 5000:

```powershell
docker run --rm -p 5000:5000 foodie:latest
```

Then open http://localhost:5000/ in a browser.

## Notes about branching / git (context)

- This repository has historically used `master` as the main branch. If you fork or change the default branch to `main`, use one of the techniques documented earlier for pushing/renaming branches.

## Security & hardening notes

- The Flask app performs a simple prefix check before serving files. That reduces risk but is not a full-proof security boundary. Don't expose this app directly to the public internet without a real static-file server in front.
- Avoid running Flask's debug server in production.
- If you add dynamic back-end functionality (APIs, database access), add proper input validation, authentication, and logging.

## Development notes

- Frontend: modify `index.html`, `assets/css/style.css`, and `assets/js/script.js`.
- Images and screen assets are located in `assets/images/`. When adding large images, consider optimizing them for the web.
- `style-guide.md` contains color and typography constants—use it as a reference for design changes.

## Troubleshooting

- Error: `src refspec main does not match any` when pushing — this means your local branch is named `master`. Either push `master` or create/rename a local `main` branch.
- If Docker fails to build, check that `requirements.txt` contains valid package names and that Docker has network access to fetch images.

## Contributing

- Small fixes: edit the files and open a pull request.
- Major changes: open an issue to discuss the plan first.

## License & contact

- This repository does not include a license file. If you plan to share or publish, add a LICENSE file (for example MIT) to avoid ambiguity.
- Contact: use your GitHub profile for contact information.

---

If you want, I can also:

- Add a short CONTRIBUTING.md and LICENSE file (MIT recommended).
- Rename the repository default branch to `main` and update local branches to match.
- Add a tiny systemd / Docker Compose example for easy local deployment.

Tell me which follow-up you'd like and I'll do it.

