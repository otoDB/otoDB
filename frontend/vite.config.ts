import { paraglideVitePlugin } from '@inlang/paraglide-js';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { execSync } from 'node:child_process';

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
			}),
			{
				name: 'watch-schema',
				configureServer(server) {
					server.watcher.add('openapi.json');
					server.watcher.on('change', (file) => {
						if (file.includes('openapi.json'))
							execSync('node_modules/.bin/openapi-typescript --enum', { stdio: 'inherit' });
					});
				}
			}
		],
		server: {
			host: '127.0.0.1',
			proxy: {
				'/media': env.PUBLIC_API_ENDPOINT || 'http://127.0.0.1:8000'
			}
		}
	};
});
