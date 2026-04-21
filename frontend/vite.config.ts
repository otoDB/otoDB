import { paraglideVitePlugin } from '@inlang/paraglide-js';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');

	return {
		plugins: [
			sveltekit(),
			tailwindcss(),
			paraglideVitePlugin({
				project: './project.inlang',
				outdir: './src/lib/paraglide',
				strategy: ['custom-userPreference', 'preferredLanguage', 'baseLocale']
			})
		],
		server: {
			host: '127.0.0.1',
			proxy: {
				'/media': env.PUBLIC_BACKEND_URL_EXTERNAL || 'http://127.0.0.1:8000'
			}
		}
	};
});
