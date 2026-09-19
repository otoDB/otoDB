import { paraglideVitePlugin } from '@inlang/paraglide-js';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { execSync } from 'node:child_process';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');

	// Optional overrides so several checkouts can run side by side on different ports
	const frontendPort = env.OTODB_DEV_FRONTEND_PORT;
	const allowedHosts = (env.OTODB_DEV_ALLOWED_HOSTS || '')
		.split(',')
		.map((host) => host.trim())
		.filter((host) => host !== '');

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
			host: env.OTODB_DEV_BIND || '127.0.0.1',
			...(frontendPort ? { port: Number(frontendPort), strictPort: true } : {}),
			...(allowedHosts.length > 0 ? { allowedHosts } : {}),
			proxy: {
				'/media': env.INTERNAL_API_ENDPOINT || env.PUBLIC_API_ENDPOINT || 'http://127.0.0.1:8000'
			}
		}
	};
});
