import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const DIST = path.join(__dirname, 'dist');

const { version } = JSON.parse(fs.readFileSync(path.join(DIST, 'manifest.json'), 'utf8'));
const zipName = `otodb-v${version}.zip`;
const zipPath = path.join(__dirname, zipName);

// Remove existing .zip to create a clean one from scratch
fs.rmSync(zipPath, { force: true });

const run = (cmd, args) => execFileSync(cmd, args, { cwd: DIST, stdio: 'inherit' });
try {
    run('7z', ['a', '-tzip', zipPath, '.']);
} catch (err) {
    if (err.code !== 'ENOENT') throw err;
    run('zip', ['-r', '-X', zipPath, '.']);
}
console.log(`Packed dist/ -> ${zipName}`);
