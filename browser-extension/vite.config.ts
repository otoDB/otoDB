import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { defineConfig } from 'vite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
    plugins: [
        svelte(),
        tailwindcss(),
        paraglideVitePlugin({
            project: '../frontend/project.inlang',
            // Write straight into the frontend's paraglide dir so `$lib/paraglide`
            // resolves to the same output in both projects.
            outdir: '../frontend/src/lib/paraglide',
            strategy: ['custom-userPreference', 'preferredLanguage', 'baseLocale']
        })
    ],
    css: {
        postcss: path.resolve(__dirname, '../frontend')
    },
    resolve: {
        alias: {
            // Shared components/utilities from the frontend
            $lib: path.resolve(__dirname, '../frontend/src/lib'),
            // Shim for `browser` from SvelteKit's `$app/environment` (set to `true`)
            '$app/environment': path.resolve(__dirname, 'src/app-environment.ts')
        }
    }
});
