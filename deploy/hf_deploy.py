#!/usr/bin/env python3
"""
One-shot deployer for TaskFlow backend to Hugging Face Spaces.

It creates TWO Docker Spaces (auth + api), uploads the code, and sets all
secrets by reading values from backend/.env. Secrets are NEVER printed and the
.env file is NEVER uploaded.

USAGE (run from anywhere):
    python deploy/hf_deploy.py

You'll be asked for:
  - your Hugging Face username
  - your Hugging Face WRITE token (input is hidden, not echoed)
  - your public frontend (Vercel) URL

Re-running is safe: Spaces are created with exist_ok, secrets/files are updated.
"""

import os
import sys
import shutil
import tempfile
import getpass
import subprocess
from pathlib import Path

# ----------------------------------------------------------------------------
# 0. Make sure huggingface_hub is installed
# ----------------------------------------------------------------------------
try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    print("Installing huggingface_hub ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub>=0.23"])
    from huggingface_hub import HfApi, create_repo


# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"
AUTH_DIR = BACKEND / "auth-service"
API_DIR = BACKEND / "api-service"
ENV_FILE = BACKEND / ".env"

AUTH_SPACE = "taskflow-auth"
API_SPACE = "taskflow-api"

IGNORE = [
    ".env", ".env.*", "*.log", "*.db", "*.sqlite*",
    "node_modules", ".git", "__pycache__", "*.pyc",
    "venv", ".venv", ".pytest_cache", "*.bak", "*.tmp",
]


def load_env(path: Path) -> dict:
    """Parse a .env file into a dict (no external deps)."""
    env = {}
    if not path.exists():
        sys.exit(f"ERROR: {path} not found. Fill in backend/.env first.")
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def space_url(user: str, space: str) -> str:
    """The public app URL for a Space (subdomain form)."""
    sub = f"{user}-{space}".lower()
    sub = "".join(c if (c.isalnum() or c == "-") else "-" for c in sub)
    return f"https://{sub}.hf.space"


def stage(src: Path) -> Path:
    """Copy a service folder to a temp dir and rename README_HF_SPACE.md -> README.md."""
    tmp = Path(tempfile.mkdtemp(prefix="hfdeploy-"))
    dst = tmp / src.name
    shutil.copytree(
        src, dst,
        ignore=shutil.ignore_patterns(
            "node_modules", ".git", "__pycache__", "*.pyc",
            "venv", ".venv", "*.log", "*.db", ".pytest_cache",
        ),
    )
    hf_readme = dst / "README_HF_SPACE.md"
    if hf_readme.exists():
        shutil.move(str(hf_readme), str(dst / "README.md"))
    return dst


def main():
    print("=" * 60)
    print(" TaskFlow → Hugging Face deployer")
    print("=" * 60)

    env = load_env(ENV_FILE)

    user = input("Hugging Face username: ").strip()
    token = getpass.getpass("Hugging Face WRITE token (hidden): ").strip()
    frontend = input("Your frontend URL (e.g. https://your-app.vercel.app): ").strip().rstrip("/")
    if not (user and token and frontend):
        sys.exit("All three values are required.")

    api = HfApi(token=token)
    auth_repo = f"{user}/{AUTH_SPACE}"
    api_repo = f"{user}/{API_SPACE}"
    auth_url = space_url(user, AUTH_SPACE)
    api_url = space_url(user, API_SPACE)

    shared_secret = env.get("BETTER_AUTH_SECRET")
    if not shared_secret:
        sys.exit("BETTER_AUTH_SECRET missing in backend/.env")

    # ---- secrets for each Space (values come from .env / computed) ----
    auth_secrets = {
        "DATABASE_URL": env.get("DATABASE_URL", ""),
        "BETTER_AUTH_SECRET": shared_secret,
        "BETTER_AUTH_URL": auth_url,
        "CORS_ORIGINS": frontend,
        "NODE_ENV": "production",
    }
    api_secrets = {
        "DATABASE_URL": env.get("DATABASE_URL", ""),
        "OPENAI_API_KEY": env.get("OPENAI_API_KEY", ""),
        "OPENAI_MODEL_NAME": env.get("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        "BETTER_AUTH_URL": auth_url,
        "USE_DAPR_INVOCATION": "false",
        "AUTH_SECRET": shared_secret,          # must match auth's BETTER_AUTH_SECRET
        "AUTH_ISSUER": auth_url,
        "CORS_ORIGINS": frontend,
        "ENVIRONMENT": "production",
        # reminder worker
        "GEMINI_API_KEY": env.get("GEMINI_API_KEY", ""),
        "GEMINI_MODEL": env.get("GEMINI_MODEL", env.get("GEMINI_MODEL_NAME", "gemini-1.5-flash")),
        "GEMINI_BASE_URL": env.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        "SMTP_HOST": env.get("SMTP_HOST", ""),
        "SMTP_PORT": env.get("SMTP_PORT", "587"),
        "SMTP_USER": env.get("SMTP_USER", ""),
        "SMTP_PASSWORD": env.get("SMTP_PASSWORD", ""),
        "SENDER_EMAIL": env.get("SENDER_EMAIL", ""),
        "APP_URL": frontend,
        "POLLING_INTERVAL_MINUTES": env.get("POLLING_INTERVAL_MINUTES", "5"),
    }

    jobs = [
        ("AUTH", auth_repo, AUTH_DIR, auth_secrets),
        ("API", api_repo, API_DIR, api_secrets),
    ]

    for label, repo, src, secrets in jobs:
        print(f"\n--- {label}: {repo} ---")
        create_repo(repo, repo_type="space", space_sdk="docker", exist_ok=True, token=token)
        print("  space ready")

        missing = [k for k, v in secrets.items() if not v]
        for key, value in secrets.items():
            api.add_space_secret(repo_id=repo, key=key, value=value)
        print(f"  set {len(secrets)} secrets" + (f"  (WARNING empty: {missing})" if missing else ""))

        staged = stage(src)
        api.upload_folder(
            folder_path=str(staged),
            repo_id=repo,
            repo_type="space",
            ignore_patterns=IGNORE,
            commit_message="Deploy via hf_deploy.py",
        )
        shutil.rmtree(staged.parent, ignore_errors=True)
        print("  code uploaded — build starting")

    print("\n" + "=" * 60)
    print(" DONE. Your Spaces are building:")
    print(f"   auth: {auth_url}/health   (page: https://huggingface.co/spaces/{auth_repo})")
    print(f"   api : {api_url}/health    (page: https://huggingface.co/spaces/{api_repo})")
    print("\n NEXT (in Vercel → Settings → Environment Variables), then redeploy:")
    print(f"   NEXT_PUBLIC_AUTH_URL = {auth_url}")
    print(f"   NEXT_PUBLIC_API_URL  = {api_url}")
    print("=" * 60)


if __name__ == "__main__":
    main()