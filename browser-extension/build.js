const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const AdmZip = require('adm-zip');

const VERSION = '1.2.1';

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

// Base manifest shared by all platforms
const manifest = {
    "manifest_version": 3,
    "name": "otoDB",
    "version": VERSION,
    "description": "otoDB is a community-driven website consisting of a collaborative user-managed database and wiki.",
    "background": {
        "scripts": ["background.js"]
    },
    "action": {
        "default_popup": "popup.html",
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
        "activeTab"
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

// Platform-specific overrides
const configs = {
    chrome: {
        background: { "service_worker": "background.js" },
    },
    firefox: {}
};

// Files to copy verbatim from src/ to dist/
const COPY_FILES = [
    'popup.html',
    'database.js',
    'background.js',
    'injector.js',
    'injected.js',
    'niconico.js',
    'niconico-embed.js',
    'niconico-embed-injected.js',
    'rules.json',
];

function clean() {
    if (fs.existsSync(DIST)) {
        fs.rmSync(DIST, { recursive: true });
    }
    fs.mkdirSync(DIST, { recursive: true });
}

function generateManifest(platform) {
    const finalManifest = { ...manifest, ...configs[platform] };
    fs.writeFileSync(
        path.join(DIST, 'manifest.json'),
        JSON.stringify(finalManifest, null, 2)
    );
    console.log(`  manifest.json (${platform})`);
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

function copyVendor() {
    const purifyPath = path.join(__dirname, 'node_modules', 'dompurify', 'dist', 'purify.min.js');
    fs.copyFileSync(purifyPath, path.join(DIST, 'purify.min.js'));
    console.log('  purify.min.js (DOMPurify)');
}

function compileCss() {
    execSync('bunx @tailwindcss/cli -i src/style.css -o dist/style.css --minify', {
        cwd: __dirname,
        stdio: 'inherit'
    });
    console.log('  style.css (Tailwind compiled)');
}

function build(platform) {
    console.log(`Building for ${platform}...`);
    clean();
    generateManifest(platform);
    copyFiles();
    copyVendor();
    compileCss();
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
} else {
    build(COMMAND);

    if (WATCH) {
        console.log('\nWatching src/ for changes...');
        let debounce = null;
        fs.watch(SRC, { recursive: true }, (event, filename) => {
            if (debounce) clearTimeout(debounce);
            debounce = setTimeout(() => {
                console.log(`\nChanged: ${filename}`);
                if (filename && filename.endsWith('.css')) {
                    compileCss();
                } else {
                    copyFiles();
                    generateManifest(COMMAND);
                }
            }, 100);
        });
    }
}
