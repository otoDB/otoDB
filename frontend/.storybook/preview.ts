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
		},
		backgrounds: { disable: true }
	},
	globalTypes: {
		lang: {
			description: 'Language',
			toolbar: {
				icon: 'globe',
				dynamicTitle: true,
				items: [
					{ value: 'en', title: 'English' },
					{ value: 'ja', title: 'Japanese' },
					{ value: 'ko', title: 'Korean' },
					{ value: 'zh-cn', title: 'Chinese (Simplified)' }
				]
			}
		}
	},
	initialGlobals: {
		lang: 'en'
	},
	decorators: [
		(story, ctx) => {
			if (ctx.globals?.lang) setLocale(ctx.globals.lang);
			return story();
		},
		(story) => {
			const s = story();
			document.body.style.backgroundColor = 'var(--otodb-color-bg-primary)';
			return s;
		},
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
