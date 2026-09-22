import { defineMain } from '@storybook/sveltekit/node';
import { mergeConfig } from 'vite';

export default defineMain({
	framework: '@storybook/sveltekit',
	stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|ts|svelte)'],
	addons: [
		'@storybook/addon-docs',
		'@storybook/addon-a11y',
		'@storybook/addon-themes',
		'@storybook/addon-vitest',
		'@storybook/addon-mcp'
	],
	staticDirs: [
		{
			from: './static',
			to: '/storybook-static'
		},
		{
			from: '../static',
			to: '/'
		}
	],
	async viteFinal(config) {
		return mergeConfig(config, {
			resolve: {
				alias: {
					'$env/dynamic/public': import.meta.resolve('./env.public.ts')
				}
			}
		});
	}
});
