import type { Preview } from '@storybook/sveltekit';
import '../src/app.css';
import { setLocale } from '../src/lib/paraglide/runtime';
import { withThemeByClassName } from '@storybook/addon-themes';

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
		withThemeByClassName({
			themes: {
				aniki: 'theme-aniki',
				sorimix: 'theme-sorimix'
			},
			defaultTheme: 'aniki'
		})
	]
};

export default preview;
