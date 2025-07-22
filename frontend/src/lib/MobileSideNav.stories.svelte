<script lang="ts" module>
	import MobileSideNav from './MobileSideNav.svelte';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { UserLevel } from '$lib/enums';
	import { fn } from 'storybook/test';

	const { Story } = defineMeta({
		title: 'MobileSideNav',
		component: MobileSideNav,
		args: {
			close: fn()
		}
	});
</script>

<Story
	name="Not Logged In"
	args={{
		user: undefined
	}}
/>

<Story
	name="Member User"
	args={{
		user: {
			csrf: 'mock-csrf-token',
			user_id: 1,
			username: 'testuser',
			level: UserLevel.MEMBER
		}
	}}
/>

<Story
	name="Editor User"
	args={{
		user: {
			csrf: 'mock-csrf-token',
			user_id: 3,
			username: 'editoruser',
			level: UserLevel.EDITOR
		}
	}}
/>

<Story
	name="Admin User"
	args={{
		user: {
			csrf: 'mock-csrf-token',
			user_id: 2,
			username: 'adminuser',
			level: UserLevel.ADMIN
		}
	}}
/>
