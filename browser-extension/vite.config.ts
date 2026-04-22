import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [
        sveltekit(),
        tailwindcss(),
        paraglideVitePlugin({
            project: './project.inlang',
            // Write straight into the frontend's paraglide dir so `$lib/paraglide`
            // resolves to the same output in both projects. (SvelteKit always
            // puts the `$lib` alias first, so a `$lib/paraglide` override alias
            // never wins against `kit.files.lib` -> `../frontend/src/lib`.)
            outdir: '../frontend/src/lib/paraglide',
            strategy: ['custom-userPreference', 'preferredLanguage', 'baseLocale']
        })
    ]
});
