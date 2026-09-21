import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import AdmZip from 'adm-zip';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const DIST = path.join(__dirname, 'dist');

const { version } = JSON.parse(fs.readFileSync(path.join(DIST, 'manifest.json'), 'utf8'));
const zipName = `otodb-v${version}.zip`;

const zip = new AdmZip();
zip.addLocalFolder(DIST);
zip.writeZip(path.join(__dirname, zipName));
console.log(`Packed dist/ -> ${zipName}`);
