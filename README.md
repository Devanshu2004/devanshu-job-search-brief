# Job Search Brief (Netlify site)

Static site for Devanshu's daily job search brief.

- `public/index.html` — the page. It asks for a passphrase once per device and decrypts the brief in the browser.
- `public/briefs.enc.json` — the last 30 briefs, encrypted (AES-256-GCM, key from PBKDF2-SHA256). Rewritten by each morning run.
- `tools/build_data.mjs` — builds `briefs.enc.json` from a folder of brief documents.
- `tools/build_page.py` — rebuilds `public/index.html` from the Claude page source.
- `netlify.toml` — tells Netlify to publish the `public` folder. There is no build step.

Never commit unencrypted briefs or the passphrase.
