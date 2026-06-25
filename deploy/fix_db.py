#!/usr/bin/env python3
"""
Diagnose (and optionally fix) the TaskFlow `tasks` table on Neon.

Reads DATABASE_URL from backend/.env. Connects directly to Neon.

  python deploy/fix_db.py              # READ-ONLY: show tables + tasks columns
  python deploy/fix_db.py --probe      # READ-ONLY: read rows like the API does and
                                       # flag NULLs in fields the response requires
  python deploy/fix_db.py --normalize  # fill NULLs in required fields + uppercase
                                       # priority on existing rows (fixes 500)
  python deploy/fix_db.py --alter      # NON-DESTRUCTIVE: add only the missing
                                       # columns (keeps existing rows)
  python deploy/fix_db.py --recreate   # DROP the tasks table (asks first), so the
                                       # API rebuilds it correctly on next restart

The default mode changes nothing. --alter preserves data. --recreate is
destructive (deletes tasks rows) and will ask for confirmation.
"""

import sys
import subprocess
from pathlib import Path

try:
    import psycopg
except ImportError:
    print("Installing psycopg ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "psycopg[binary]"])
    import psycopg

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = REPO_ROOT / "backend" / ".env"

# Columns the current API Task model expects (backend/api-service/models.py)
EXPECTED = [
    "id", "user_id", "title", "description", "status", "created_at", "updated_at",
    "completed_at", "completed", "priority", "tags", "due_date", "recurrence_rule",
    "parent_task_id", "reminder_time", "reminder_offset", "recurrence_pattern",
    "last_completed_at",
]

# Non-destructive DDL to add a column if it's missing (types match the model and
# the existing timezone-naive timestamp columns).
COLUMN_DDL = {
    "status": "ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'pending'",
    "completed_at": "ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP",
    "recurrence_rule": "ADD COLUMN IF NOT EXISTS recurrence_rule JSONB",
    "parent_task_id": "ADD COLUMN IF NOT EXISTS parent_task_id INTEGER REFERENCES tasks(id)",
    "completed": "ADD COLUMN IF NOT EXISTS completed BOOLEAN NOT NULL DEFAULT false",
    "priority": "ADD COLUMN IF NOT EXISTS priority VARCHAR(20)",
    "tags": "ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::jsonb",
    "due_date": "ADD COLUMN IF NOT EXISTS due_date TIMESTAMP",
    "reminder_time": "ADD COLUMN IF NOT EXISTS reminder_time TIMESTAMP",
    "reminder_offset": "ADD COLUMN IF NOT EXISTS reminder_offset VARCHAR",
    "recurrence_pattern": "ADD COLUMN IF NOT EXISTS recurrence_pattern VARCHAR(20) NOT NULL DEFAULT 'none'",
    "last_completed_at": "ADD COLUMN IF NOT EXISTS last_completed_at TIMESTAMP",
    "description": "ADD COLUMN IF NOT EXISTS description VARCHAR",
    "created_at": "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP",
    "updated_at": "ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP",
}


def get_database_url() -> str:
    if not ENV_FILE.exists():
        sys.exit(f"ERROR: {ENV_FILE} not found.")
    for raw in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("DATABASE_URL=") and not line.startswith("#"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ERROR: DATABASE_URL not found in backend/.env")


def main():
    recreate = "--recreate" in sys.argv
    alter = "--alter" in sys.argv
    probe = "--probe" in sys.argv
    normalize = "--normalize" in sys.argv
    url = get_database_url()

    # Fields TaskResponse requires to be non-null (a NULL here causes a 500)
    REQUIRED_NOTNULL = [
        "id", "user_id", "title", "completed", "created_at", "updated_at",
        "priority", "tags", "recurrence_pattern",
    ]

    # psycopg wants 'postgresql://' (strip any '+driver')
    conninfo = url.replace("postgresql+psycopg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")

    with psycopg.connect(conninfo) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select table_name from information_schema.tables "
                "where table_schema='public' order by table_name"
            )
            tables = [r[0] for r in cur.fetchall()]
            print("\nPublic tables:", ", ".join(tables) or "(none)")

            if "tasks" not in tables:
                print("\n'tasks' table does NOT exist yet — the API will create it on startup.")
                print("If you see 500s, restart the API Space so startup runs.")
                return

            cur.execute(
                "select column_name, data_type from information_schema.columns "
                "where table_schema='public' and table_name='tasks' order by ordinal_position"
            )
            cols = cur.fetchall()
            have = {c[0] for c in cols}
            print("\nCurrent 'tasks' columns:")
            for name, dtype in cols:
                print(f"  - {name} ({dtype})")

            missing = [c for c in EXPECTED if c not in have]
            cur.execute("select count(*) from tasks")
            rows = cur.fetchone()[0]
            print(f"\nRows in tasks: {rows}")
            print("MISSING columns the API needs:", ", ".join(missing) or "(none — schema looks OK)")

            if probe:
                print("\n--probe: reading rows the way the API does...")
                try:
                    cur.execute(
                        "select " + ", ".join(REQUIRED_NOTNULL)
                        + ", status, recurrence_rule, parent_task_id from tasks"
                    )
                    fetched = cur.fetchall()
                    names = [d.name for d in cur.description]
                except Exception as e:
                    print("  DB read FAILED:", repr(e))
                    print("  -> the 500 is a database read error (shown above).")
                    return
                bad = False
                for r in fetched:
                    row = dict(zip(names, r))
                    nulls = [k for k in REQUIRED_NOTNULL if row.get(k) is None]
                    if nulls:
                        bad = True
                    flag = ("   <-- NULL in required: " + ", ".join(nulls)) if nulls else ""
                    print(f"  id={row.get('id')} priority={row.get('priority')!r} "
                          f"tags={row.get('tags')!r} recurrence_pattern={row.get('recurrence_pattern')!r} "
                          f"completed={row.get('completed')!r} status={row.get('status')!r}{flag}")
                if bad:
                    print("\n>>> Found NULLs in fields the API response REQUIRES — that is the 500.")
                    print("    Fix it (keeps data):  python deploy/fix_db.py --normalize")
                else:
                    print("\nNo NULLs in required fields, and the read worked.")
                    print("So the 500 is NOT bad data — it's API-side. Send me the API Space")
                    print("logs (the Python traceback shown when you load tasks).")
                return

            if normalize:
                print("\n--normalize: filling NULLs in required fields + uppercasing priority...")
                stmts = [
                    "UPDATE tasks SET priority='MEDIUM' WHERE priority IS NULL",
                    "UPDATE tasks SET priority=UPPER(priority) WHERE priority IS NOT NULL",
                    "UPDATE tasks SET tags='[]'::jsonb WHERE tags IS NULL",
                    "UPDATE tasks SET recurrence_pattern='none' WHERE recurrence_pattern IS NULL",
                    "UPDATE tasks SET status='pending' WHERE status IS NULL",
                    "UPDATE tasks SET completed=false WHERE completed IS NULL",
                    "UPDATE tasks SET created_at=NOW() WHERE created_at IS NULL",
                    "UPDATE tasks SET updated_at=NOW() WHERE updated_at IS NULL",
                ]
                for s in stmts:
                    cur.execute(s)
                    print(f"  {cur.rowcount:>3} rows  <-  {s}")
                conn.commit()
                print("\nDone. Reload your site — tasks should load now (no restart needed).")
                return

            if alter:
                if not missing:
                    print("\nNothing to do — all expected columns already exist.")
                    return
                print("\n--alter: adding missing columns (existing rows are kept)...")
                for col in missing:
                    ddl = COLUMN_DDL.get(col)
                    if not ddl:
                        print(f"  ! no DDL defined for '{col}' — skipping (tell me)")
                        continue
                    cur.execute(f"ALTER TABLE tasks {ddl}")
                    print(f"  + {col}")
                conn.commit()
                cur.execute(
                    "select column_name from information_schema.columns "
                    "where table_schema='public' and table_name='tasks'"
                )
                now_have = {r[0] for r in cur.fetchall()}
                still = [c for c in EXPECTED if c not in now_have]
                print("\nDone. Still missing:", ", ".join(still) or "(none — schema matches now)")
                print("Reload your site — tasks should load now (no restart needed).")
                return

            if not recreate:
                if missing:
                    print("\n>>> Diagnosis: schema drift. The API crashes (500) selecting columns")
                    print("    that don't exist. Run with --alter to add them (keeps data), OR")
                    print("    --recreate to drop & rebuild.")
                return

            # --recreate path
            print(f"\n--recreate: this will DROP the tasks table (and {rows} rows) so the API")
            print("rebuilds it with the correct schema on next restart. The 'user'/auth tables")
            print("are NOT touched.")
            if input("Type 'yes' to proceed: ").strip().lower() != "yes":
                print("Aborted. Nothing changed.")
                return
            cur.execute("DROP TABLE IF EXISTS tasks CASCADE")
            conn.commit()
            print("Dropped 'tasks' (CASCADE). Now RESTART the API Space")
            print("(HF Space → Settings → Factory reboot) and reload your site.")


if __name__ == "__main__":
    main()
