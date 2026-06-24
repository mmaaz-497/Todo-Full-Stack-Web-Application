#!/bin/sh
# Container entrypoint for the TaskFlow API Hugging Face Space.
#
# Runs TWO processes in one container:
#   1. The email-reminder worker (polls Neon for due reminders -> sends SMTP)
#   2. The FastAPI API (uvicorn)
#
# The worker is started in the background. If its required env vars are missing
# (DATABASE_URL, GEMINI_API_KEY, SMTP_HOST/USER/PASSWORD, SENDER_EMAIL, APP_URL)
# it will exit on startup, but the API keeps serving normally.

# Start the reminder worker in the background (runs from its own dir so its
# internal absolute imports resolve).
( cd reminder_worker && python main.py ) &

# Start the API on the port Hugging Face provides (falls back to 8000 locally).
# Single worker so we never run duplicate schedulers if this file is reused.
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
