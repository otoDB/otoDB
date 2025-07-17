<script lang="ts" module>
	import SideNav from './SideNav.svelte';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { type ComponentProps } from 'svelte';

	const { Story } = defineMeta({
		title: 'SideNav',
		component: SideNav
	});
</script>

<Story
	name="Not Logged In"
	args={{
		width: '256px',
		user: undefined,
		stats: [0, 0, 0, 0]
	}}
/>
