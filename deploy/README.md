# One-command Hugging Face deploy

`hf_deploy.py` creates both Spaces (auth + api), uploads the code, and sets all
secrets from `backend/.env`. Secrets are never printed; `.env` is never uploaded.

## Run it

```bash
python deploy/hf_deploy.py
```

It asks for three things:
1. **Hugging Face username**
2. **Hugging Face WRITE token** (input hidden — get one at
   https://huggingface.co/settings/tokens)
3. **Your frontend URL** (e.g. `https://your-app.vercel.app`)

When it finishes it prints the two Space URLs and the two Vercel variables to set.

## After it runs

1. Open each printed `…/health` URL to confirm the Spaces are up.
2. In **Vercel → Settings → Environment Variables**, set `NEXT_PUBLIC_AUTH_URL`
   and `NEXT_PUBLIC_API_URL` to the printed values, then **redeploy** the frontend.
3. Log in on your site and create a task to verify.

Re-running the script is safe — it updates the existing Spaces.

Full manual walkthrough (if you prefer clicking): `docs/HUGGINGFACE_DEPLOYMENT.md`.
