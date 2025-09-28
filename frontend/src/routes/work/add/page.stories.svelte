<script lang="ts" module>
	import Page from './+page.svelte';
	import { defineMeta } from '@storybook/addon-svelte-csf';

	const { Story } = defineMeta({
		title: 'Pages/Work/Add',
		component: Page
	});
</script>

<Story
	name="Default"
	args={{
		data: {
			title: null,
			link: null
		},
		form: null
	}}
/>

<Story
	name="With Prefilled URL"
	args={{
		data: {
			title: null,
			link: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
		},
		form: null
	}}
/>
