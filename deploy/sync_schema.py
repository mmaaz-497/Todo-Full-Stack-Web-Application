#!/usr/bin/env python3
"""
Make the Neon `tasks` table match the API's Task model exactly by adding any
missing columns (with the model's own types). Non-destructive: only ADD COLUMN
IF NOT EXISTS — never drops or alters existing columns/data.

  python deploy/sync_schema.py            # show what's missing (read-only)
  python deploy/sync_schema.py --apply    # add the missing columns
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "backend" / "api-service"
ENV = ROOT / "backend" / ".env"


def database_url() -> str:
    for line in ENV.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("DATABASE_URL=") and not s.startswith("#"):
            return s.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("DATABASE_URL not found in backend/.env")


def main():
    apply = "--apply" in sys.argv

    # Force psycopg3 driver (installed) for this local run.
    url = database_url()
    url = url.replace("postgresql+psycopg2://", "postgresql://").replace("postgresql://", "postgresql+psycopg://")
    os.environ["DATABASE_URL"] = url

    sys.path.insert(0, str(API_DIR))
    from sqlalchemy import inspect, text
    from db import engine
    from models import Task  # registers the table on the metadata

    insp = inspect(engine)
    existing = {c["name"] for c in insp.get_columns("tasks")}
    dialect = engine.dialect

    missing = [c for c in Task.__table__.columns if c.name not in existing]
    if not missing:
        print("tasks table already matches the model. Nothing to add.")
        return

    print("Missing columns the API model needs:")
    ddls = []
    for col in missing:
        coltype = col.type.compile(dialect)
        ddls.append((col.name, coltype))
        print(f"  - {col.name} {coltype}")

    if not apply:
        print("\nRead-only. Re-run with --apply to add them.")
        return

    with engine.begin() as conn:
        for name, coltype in ddls:
            conn.execute(text(f'ALTER TABLE tasks ADD COLUMN IF NOT EXISTS "{name}" {coltype}'))
            print(f"  + added {name} {coltype}")
    print("\nDone. Reload your site — task loading should work now.")


if __name__ == "__main__":
    main()
