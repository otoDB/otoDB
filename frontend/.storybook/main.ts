import { defineMain } from '@storybook/sveltekit/node';

export default defineMain({
	framework: '@storybook/sveltekit',
	stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|ts|svelte)'],
	addons: ['@storybook/addon-docs', '@storybook/addon-a11y', '@storybook/addon-themes'],
	staticDirs: [
		{
			from: './static',
			to: '/storybook-static'
		},
		{
			from: '../static',
			to: '/'
		}
	]
});
