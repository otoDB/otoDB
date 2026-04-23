<script module>
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Pager from './Pager.svelte';

	const { Story } = defineMeta({
		title: 'Lib/Pager',
		component: Pager,
		tags: ['autodocs'],
		argTypes: {
			page: { control: { type: 'number', min: 1 } },
			page_size: { control: { type: 'number', min: 1 } },
			n_count: { control: { type: 'number', min: 0 } },
			window_size: { control: { type: 'number', min: 1 } },
			base_url: { control: 'text' }
		},
		args: {
			page: 5,
			page_size: 20,
			n_count: 200,
			window_size: 2
		}
	});
</script>

<Story name="Default" />

<Story name="First Page" args={{ page: 1, page_size: 20, n_count: 200 }} />

<Story name="Last Page" args={{ page: 10, page_size: 20, n_count: 200 }} />

<Story name="Few Pages" args={{ page: 2, page_size: 20, n_count: 60 }} />

<Story name="Single Page" args={{ page: 1, page_size: 20, n_count: 15 }} />

<Story name="Narrow Window" args={{ page: 5, page_size: 20, n_count: 200, window_size: 1 }} />

<Story name="Wide Window" args={{ page: 5, page_size: 20, n_count: 200, window_size: 4 }} />

<Story
	name="With Base URL"
	args={{ page: 5, page_size: 20, n_count: 200, base_url: 'https://example.com/posts?tag=foo' }}
/>
