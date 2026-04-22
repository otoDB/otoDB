import adapter from 'sveltekit-adapter-chrome-extension';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    preprocess: vitePreprocess(),

    kit: {
        adapter: adapter({
            pages: 'dist',
            assets: 'dist',
            fallback: undefined,
            precompress: false,
            strict: true
        }),
        router: { type: 'hash' },
        // Chrome refuses to load extensions whose top-level directories
        // start with an underscore, so override SvelteKit's default `_app`.
        appDir: 'app',
        files: {
            lib: '../frontend/src/lib'
        }
        // Extension-only code can live under `src/local/` and be imported
        // via `$ext/…` — uncomment when needed.
        // alias: {
        //     $ext: './src/local',
        //     '$ext/*': './src/local/*'
        // }
    }
};

export default config;
