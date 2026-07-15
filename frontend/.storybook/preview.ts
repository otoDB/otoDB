import { withThemeByDataAttribute } from '@storybook/addon-themes';
import type { Preview } from '@storybook/sveltekit';
import { initialize as mswInitialize, mswLoader } from 'msw-storybook-addon';
import {
	type Locale,
	overwriteGetLocale,
	overwriteSetLocale,
	setLocale
} from '../src/lib/paraglide/runtime';

import '../src/app.css';

mswInitialize({
	onUnhandledRequest(req, p) {
		if (/src/g.test(req.url) || /@id/g.test(req.url)) return;
		p.warning();
	}
});

let localeState: Locale | undefined = undefined;
overwriteGetLocale(() => localeState || 'en');
overwriteSetLocale((nw) => {
	if (localeState !== undefined && localeState !== nw) window.location.reload();
	localeState = nw;
});

const preview: Preview = {
	loaders: [mswLoader],
	parameters: {
		controls: {
			matchers: {
				color: /(background|color)$/i,
				date: /Date$/i
			}
		},

		a11y: {
			// 'todo' - show a11y violations in the test UI only
			// 'error' - fail CI on a11y violations
			// 'off' - skip a11y checks entirely
			test: 'todo'
		}
	},
	globalTypes: {
		locale: {
			description: 'Language',
			defaultValue: 'en' satisfies Locale,
			toolbar: {
				icon: 'globe',
				dynamicTitle: true,
				items: [
					{ value: 'en', title: 'English' },
					{ value: 'ja', title: 'Japanese' },
					{ value: 'ko', title: 'Korean' },
					{ value: 'zh-cn', title: 'Chinese (Simplified)' }
				] satisfies { value: Locale; title: string }[]
			}
		}
	},
	decorators: [
		(story) => {
			const s = story();
			document.body.style.backgroundColor = 'var(--otodb-color-bg-primary)';
			return s;
		},
		withThemeByDataAttribute({
			themes: {
				'plain-dark': 'plain-dark',
				'plain-light': 'plain-light',
				'aniki': 'aniki',
				'otogroove': 'otogroove',
				'retro-voyage': 'retro-voyage',
				'sorimix': 'sorimix',
				'resample': 'resample'
			},
			defaultTheme: 'plain-dark',
			attributeName: 'data-theme'
		}),
		(storyFn, context) => {
			const currentLocale = context.globals?.locale as Locale | undefined;
			if (currentLocale) setLocale(currentLocale);
			return storyFn();
		}
	]
};

export default preview;
