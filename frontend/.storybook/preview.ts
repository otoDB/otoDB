import type { Preview, SvelteRenderer } from '@storybook/sveltekit';
import { setLocale } from '../src/lib/paraglide/runtime';
import { withThemeByDataAttribute } from '@storybook/addon-themes';
import '../src/app.css';

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
		(story, ctx) => {
			setLocale(ctx.globals?.lang || ctx.globals?.lang);
			return story();
		},
		withThemeByDataAttribute<SvelteRenderer>({
			defaultTheme: 'dark',
			themes: {
				light: 'light',
				dark: 'dark'
			}
		})
	]
};

export default preview;
