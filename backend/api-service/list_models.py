"""List all available Gemini models"""
import google.generativeai as genai
from pathlib import Path

# Read API key
env_path = Path(__file__).parent / ".env"
api_key = None
with open(env_path, 'r') as f:
    for line in f:
        if line.startswith('GOOGLE_API_KEY='):
            api_key = line.split('=', 1)[1].strip()
            break

print(f"API Key: {api_key[:15]}...")
print("-" * 60)

genai.configure(api_key=api_key)

print("Fetching available models from Google...")
print("=" * 60)

try:
    models = genai.list_models()
    generation_models = []

    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            generation_models.append(m.name)
            print(f"  {m.name}")

    print("\n" + "=" * 60)
    print(f"Found {len(generation_models)} models")

    if generation_models:
        # Get just the model name without 'models/' prefix
        best_model = generation_models[0].replace('models/', '')
        print(f"\nRecommended: {best_model}")
        print(f"\nUpdate your .env file to:")
        print(f"GEMINI_MODEL_NAME={best_model}")

except Exception as e:
    print(f"ERROR: {type(e).__name__}")
    print(f"Message: {str(e)[:200]}")
