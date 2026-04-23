import type { Preview } from '@storybook/sveltekit';
import '../src/app.css';
import { setLocale } from '../src/lib/paraglide/runtime';
import { withThemeByDataAttribute } from '@storybook/addon-themes';

const preview: Preview = {
	parameters: {
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i
			}
		}
	},
	globalTypes: {
		lang: {
			description: 'Language',
			toolbar: {
				icon: 'globe',
				dynamicTitle: true,
				items: [
					{ value: 'en', title: 'en' },
					{ value: 'ja', title: 'ja' },
					{ value: 'ko', title: 'ko' },
					{ value: 'zh-cn', title: 'zh-cn' }
				]
			}
		}
	},
	initialGlobals: {
		lang: 'en'
	},
	decorators: [
		/*
		(story, ctx) => {
			setLocale(ctx.globals?.lang || ctx.globals?.lang);
			return story();
		}
		*/
		withThemeByDataAttribute({
			themes: {
				'default': 'default',
				'aniki': 'aniki',
				'otogroove': 'otogroove',
				'retro-voyage': 'retro-voyage',
				'sorimix': 'sorimix',
				'resample': 'resample'
			},
			defaultTheme: 'default',
			attributeName: 'data-theme'
		})
	]
};

export default preview;
