// Builds public/briefs.enc.json from a folder of brief documents.
// Usage: BRIEF_PASSPHRASE='...' node tools/build_data.mjs <folder-with-YYYY-MM-DD.json> [public/briefs.enc.json]
// Encryption: PBKDF2-SHA256 (250,000 rounds) -> AES-256-GCM. The page decrypts in the browser.
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { randomBytes, pbkdf2Sync, createCipheriv } from 'node:crypto';

const dir = process.argv[2];
const out = process.argv[3] || 'public/briefs.enc.json';
const pass = (process.env.BRIEF_PASSPHRASE || '').trim();
if (!dir || !pass) { console.error('Need a folder argument and BRIEF_PASSPHRASE.'); process.exit(1); }

let briefs = readdirSync(dir).filter(f => /^\d{4}-\d{2}-\d{2}\.json$/.test(f))
  .map(f => JSON.parse(readFileSync(join(dir, f), 'utf8')))
  .filter(b => b && typeof b.date === 'string');
if (briefs.some(b => !b.sample)) briefs = briefs.filter(b => !b.sample);
briefs.sort((a, b) => (a.date < b.date ? 1 : -1));
briefs = briefs.slice(0, 30);

const ITER = 250000;
const salt = randomBytes(16), iv = randomBytes(12);
const key = pbkdf2Sync(pass, salt, ITER, 32, 'sha256');
const cipher = createCipheriv('aes-256-gcm', key, iv);
const ct = Buffer.concat([cipher.update(JSON.stringify({ briefs }), 'utf8'), cipher.final(), cipher.getAuthTag()]);
writeFileSync(out, JSON.stringify({ v: 1, kdf: 'PBKDF2-SHA256', iter: ITER, salt: salt.toString('base64'), iv: iv.toString('base64'), ct: ct.toString('base64'), updated: new Date().toISOString() }));
console.log(`Wrote ${out}: ${briefs.length} brief(s), newest ${briefs[0] ? briefs[0].date : 'none'}`);
