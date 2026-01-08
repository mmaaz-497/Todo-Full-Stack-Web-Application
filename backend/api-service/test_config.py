"""Test what the config module is loading"""
from app.config import settings

print("="*60)
print("CONFIGURATION VALUES:")
print("="*60)
print(f"GOOGLE_API_KEY: {settings.GOOGLE_API_KEY[:20]}...")
print(f"Full key length: {len(settings.GOOGLE_API_KEY)}")
print(f"GEMINI_MODEL_NAME: {settings.GEMINI_MODEL_NAME}")
print(f"GEMINI_TEMPERATURE: {settings.GEMINI_TEMPERATURE}")
print(f"GEMINI_MAX_TOKENS: {settings.GEMINI_MAX_TOKENS}")
print("="*60)

# Compare with .env file directly
from pathlib import Path
env_path = Path(__file__).parent / ".env"
print(f"\nReading .env file directly:")
with open(env_path, 'r') as f:
    for line in f:
        if 'GOOGLE_API_KEY' in line or 'GEMINI_MODEL' in line:
            print(f"  {line.strip()}")

print("\nDo they match?", "YES" if f"GOOGLE_API_KEY={settings.GOOGLE_API_KEY}" in open(env_path).read() else "NO")
