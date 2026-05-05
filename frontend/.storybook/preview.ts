import { withThemeByDataAttribute } from '@storybook/addon-themes';
import type { Preview } from '@storybook/sveltekit';
import { initialize, mswLoader } from 'msw-storybook-addon';
import { useEffect } from 'storybook/preview-api';
import { setLocale } from '../src/lib/paraglide/runtime';
import '../src/app.css';

initialize();

const preview: Preview = {
	loaders: [mswLoader],
	parameters: {
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i
			}
		}
	},
	globalTypes: {
		locale: {
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
			},
			defaultValue: 'en'
		}
	},
	decorators: [
		(storyFn, context) => {
			const locale = context.globals?.locale;

			useEffect(() => {
				// if (locale) setLocale(locale);
			}, [locale]);

			return storyFn();
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
