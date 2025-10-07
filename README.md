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

## Infrastructure as Code (IaC) — Terraform & DevOps

There is an `Iac/` directory that contains a Terraform configuration used to provision a small AWS infrastructure for running this Flask app inside ECS Fargate. Below is a concise summary of what's present and how the DevOps pieces fit together.

Folder and important files

- `Iac/main.tf` — primary Terraform configuration (provider + resources).
- `Iac/.terraform.lock.hcl` — provider dependency lock file (auto-managed by `terraform init`).
- `Iac/terraform.tfstate` and `Iac/terraform.tfstate.backup` — Terraform state snapshots (do not store secrets in state; consider remote state).

What the Terraform config provisions (summary)

- AWS provider configured with `region = "ap-south-1"` (modify in `main.tf` as needed).
- Networking: VPC (`aws_vpc`), a public subnet, Internet Gateway, Route Table and association.
- Security group allowing inbound TCP on port 5000 (this is the port the Flask app listens on).
- ECS: an ECS cluster (`aws_ecs_cluster`) and an ECS Fargate service (`aws_ecs_service`) running a single task.
- IAM: an execution role for ECS tasks (`aws_iam_role` + managed policy attachment) so the task can run with proper permissions.
- Task definition references container image `tuheen27/devops-projects:latest` and maps container port 5000.

Key implementation notes / caveats

- The container image name in the Terraform task definition is `tuheen27/devops-projects:latest`. You must build and push this image to a registry (Docker Hub, ECR, etc.) accessible from your ECS tasks before creating/updating the service.
- The security group currently allows port 5000 from anywhere. For production, restrict that to a load balancer or specific CIDR ranges.
- The repo contains a local `terraform.tfstate`. For team use, switch to remote state (S3 backend + DynamoDB locking) to avoid state conflicts:
  - Example backend: S3 bucket for state and DynamoDB table for state locking.

Recommended local Terraform workflow (PowerShell)

1. Install Terraform (use the required version). `main.tf` declares `required_version = ">= 1.5.0"`. The state file shows it was last used with Terraform `1.13.3` — use the same or a newer compatible Terraform release.

2. Configure AWS credentials (one of):

```powershell
# Option A: environment variables (temporary session)
$env:AWS_ACCESS_KEY_ID = "<your-access-key>"
$env:AWS_SECRET_ACCESS_KEY = "<your-secret>"
$env:AWS_DEFAULT_REGION = "ap-south-1"

# Option B: use named profile (recommended for local dev)
aws configure --profile your-profile-name
```

3. Init, plan and apply inside the `Iac` folder:

```powershell
cd Iac
terraform init
terraform plan -out plan.tfplan
terraform apply "plan.tfplan"
```

4. To tear down the environment:

```powershell
terraform destroy -auto-approve
```

Docker image build & push (so ECS can pull it)

You have two common choices: Docker Hub or AWS ECR.

- Docker Hub (simple):

```powershell
docker build -t tuheen27/devops-projects:latest ..\
docker login
docker push tuheen27/devops-projects:latest
```

- AWS ECR (recommended for private images in AWS):

1) Create an ECR repository (one-time):

```powershell
aws ecr create-repository --repository-name devops-projects --region ap-south-1
```

2) Tag and push the image (the AWS CLI can print a login command):

```powershell
$(aws ecr get-login-password --region ap-south-1) | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com
docker tag tuheen27/devops-projects:latest <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/devops-projects:latest
docker push <aws_account_id>.dkr.ecr.ap-south-1.amazonaws.com/devops-projects:latest
```

CI/CD recommendations

- Build & push container image in CI (GitHub Actions / GitLab CI / Jenkins) on push to `master`/`main`.
- Run `terraform fmt` and `terraform validate` as part of the pipeline.
- Create a pipeline job that runs `terraform plan` and stores the plan as an artifact for review. Require a manual approval step before `terraform apply` in production.
- Use the official `hashicorp/setup-terraform` and `aws-actions/configure-aws-credentials` GitHub Actions to set up the environment and run Terraform.

State management & security

- Do NOT commit secrets (AWS keys, DB passwords) to the repository.
- Move from local state to a remote backend (S3 + DynamoDB locks) for team collaboration.
- Enable versioning on the S3 backend bucket to be able to recover from accidental state changes.

Quick example of GitHub Actions steps (outline)

1) Build & push image
2) Run `terraform init` and `terraform plan` (artifact plan)
3) Manual approval
4) `terraform apply`

If you'd like, I can create a GitHub Actions workflow file in `.github/workflows/` that builds the image and runs Terraform (with a manual approval step for apply). I can also help convert the Terraform local state to an S3 backend and add example `backend` configuration.

## Contributing

- Small fixes: edit the files and open a pull request.
- Major changes: open an issue to discuss the plan first.




