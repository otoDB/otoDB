import type { Preview } from '@storybook/sveltekit';
import '../src/app.css';
import { setLocale } from '../src/lib/paraglide/runtime';

const preview: Preview = {
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
			setLocale(ctx.globals?.lang);
			return story();
		}
	]
};

export default preview;
