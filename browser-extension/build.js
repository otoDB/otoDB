import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import AdmZip from 'adm-zip';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const VERSION = '1.2.3';

const COMMANDS = ['chrome', 'firefox', 'pack'];
const COMMAND = process.argv.find(a => COMMANDS.includes(a));
const WATCH = process.argv.includes('--watch');

if (!COMMAND) {
    console.error('Usage: node build.js <chrome|firefox> [--watch]');
    console.error('       node build.js pack');
    process.exit(1);
}

const SRC = path.join(__dirname, 'src');
const DIST = path.join(__dirname, 'dist');

const manifest = {
    "manifest_version": 3,
    "name": "otoDB",
    "version": VERSION,
    "description": "otoDB is a community-driven website consisting of a collaborative user-managed database and wiki.",
    "background": {
        "scripts": ["background.js"]
    },
    "action": {
        "default_popup": "index.html",
        "default_title": "otoDB"
    },
    "content_scripts": [
        {
            "matches": ["https://*.nicovideo.jp/*"],
            "js": ["niconico.js"]
        },
        {
            "matches": ["https://embed.nicovideo.jp/watch/*"],
            "js": ["niconico-embed.js"],
            "run_at": "document_idle",
            "all_frames": true
        },
        {
            "matches": ["https://*.nicovideo.jp/*"],
            "js": ["injector.js"],
            "run_at": "document_start",
            "all_frames": true
        },
        {
            "matches": ["https://otodb.net/*"],
            "js": ["otodb-prefs.js"],
            "run_at": "document_start"
        }
    ],
    "web_accessible_resources": [
        {
            "resources": ["injected.js", "niconico-embed-injected.js"],
            "matches": ["https://*.nicovideo.jp/*"]
        }
    ],
    "permissions": [
        "declarativeNetRequestWithHostAccess",
        "cookies",
        "activeTab",
        "storage"
    ],
    "host_permissions": [
        "https://otodb.net/*",
        "https://*.nicovideo.jp/*",
        "https://*.nicoseiga.jp/*",
        "https://www.nicochart.jp/*",
    ],
    "declarative_net_request": {
        "rule_resources": [
            {
                "id": "ruleset",
                "enabled": true,
                "path": "rules.json"
            }
        ]
    },
    "browser_specific_settings": {
        "gecko": {
            "id": "{717c1436-7545-4acd-bed8-a473bac7698b}"
        }
    }
};

const configs = {
    chrome: { background: { "service_worker": "background.js" } },
    firefox: {}
};

// Non-Svelte files copied verbatim from src/ - content scripts and network
// rules that MV3 loads outside of the popup bundle.
const COPY_FILES = [
    'background.js',
    'injector.js',
    'injected.js',
    'niconico.js',
    'niconico-embed.js',
    'niconico-embed-injected.js',
    'otodb-prefs.js',
    'rules.json'
];

function clean() {
    if (fs.existsSync(DIST)) fs.rmSync(DIST, { recursive: true });
    fs.mkdirSync(DIST, { recursive: true });
}

function runVite() {
    const result = spawnSync('bunx', ['--bun', 'vite', 'build'], {
        cwd: __dirname,
        stdio: 'inherit',
        shell: true
    });
    if (result.status !== 0) throw new Error('vite build failed');
}

function copyFiles() {
    for (const file of COPY_FILES) {
        const srcPath = path.join(SRC, file);
        if (fs.existsSync(srcPath)) {
            fs.copyFileSync(srcPath, path.join(DIST, file));
            console.log(`  ${file}`);
        } else {
            console.warn(`  WARNING: ${file} not found in src/`);
        }
    }
}

function generateManifest(platform) {
    const finalManifest = { ...manifest, ...configs[platform] };
    fs.writeFileSync(
        path.join(DIST, 'manifest.json'),
        JSON.stringify(finalManifest, null, 2)
    );
    console.log(`  manifest.json (${platform})`);
}

function build(platform) {
    console.log(`Building for ${platform}...`);
    clean();
    runVite();
    copyFiles();
    generateManifest(platform);
    console.log(`\nDone -> dist/`);
}

function pack() {
    for (const platform of ['chrome', 'firefox']) {
        build(platform);
        const zipName = `otodb-${platform}-v${VERSION}.zip`;
        const zipPath = path.join(__dirname, zipName);
        if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);
        console.log(`\nZipping ${platform}...`);
        const zip = new AdmZip();
        zip.addLocalFolder(DIST);
        zip.writeZip(zipPath);
        console.log(`  -> ${zipName}`);
    }
    console.log('\nPack complete!');
}

if (COMMAND === 'pack') {
    pack();
} else if (WATCH) {
    build(COMMAND);
    console.log('\nWatching src/ for changes...');
    const vite = spawn('bunx', ['--bun', 'vite', 'build', '--watch'], {
        cwd: __dirname,
        stdio: 'inherit',
        shell: true
    });
    let debounce = null;
    fs.watch(SRC, { recursive: true }, (_event, filename) => {
        if (!filename || COPY_FILES.every(f => !filename.endsWith(f))) return;
        if (debounce) clearTimeout(debounce);
        debounce = setTimeout(() => {
            console.log(`\nChanged: ${filename}`);
            copyFiles();
            generateManifest(COMMAND);
        }, 100);
    });
    vite.on('exit', code => process.exit(code ?? 0));
} else {
    build(COMMAND);
}
