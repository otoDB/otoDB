<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { WorkTagCategory } from '$lib/schema';
	import WorkTag from './WorkTag.svelte';

	const baseTag = {
		id: 1,
		slug: 'example-tag',
		lang_prefs: [],
		name: 'Example Tag'
	};

	const { Story } = defineMeta({
		title: 'WorkTag',
		component: WorkTag,
		args: {
			tag: { ...baseTag, category: WorkTagCategory.General },
			selected: false,
			fade: false,
			forTree: false
		}
	});
</script>

<Story name="General" args={{ tag: { ...baseTag, category: WorkTagCategory.General } }} />

<Story name="Event" args={{ tag: { ...baseTag, category: WorkTagCategory.Event } }} />

<Story name="Song" args={{ tag: { ...baseTag, category: WorkTagCategory.Song } }} />

<Story name="Source" args={{ tag: { ...baseTag, category: WorkTagCategory.Source } }} />

<Story name="Media" args={{ tag: { ...baseTag, category: WorkTagCategory.Media } }} />

<Story name="Meta" args={{ tag: { ...baseTag, category: WorkTagCategory.Meta } }} />

<Story
	name="Creator"
	args={{ tag: { ...baseTag, category: WorkTagCategory.Creator, creator_roles: null } }}
/>

<Story
	name="Creator with Roles"
	args={{
		tag: {
			...baseTag,
			category: WorkTagCategory.Creator,
			creator_roles: [1, 8]
		}
	}}
/>

<Story
	name="Sample Override"
	args={{
		tag: { ...baseTag, category: WorkTagCategory.Creator, sample: true, creator_roles: null }
	}}
/>

<Story name="Temporary" args={{ tag: { ...baseTag, id: 0, category: WorkTagCategory.General } }} />

<Story name="Faded" args={{ tag: { ...baseTag, category: WorkTagCategory.General }, fade: true }} />

<Story
	name="Selectable"
	args={{
		tag: { ...baseTag, category: WorkTagCategory.General },
		onclick: () => {}
	}}
/>

<Story
	name="Selected"
	args={{
		tag: { ...baseTag, category: WorkTagCategory.General },
		selected: true,
		onclick: () => {}
	}}
/>

<Story
	name="For Tree"
	args={{ tag: { ...baseTag, category: WorkTagCategory.General }, forTree: true }}
/>

<Story
	name="With Lang Prefs"
	args={{
		tag: {
			...baseTag,
			category: WorkTagCategory.General,
			lang_prefs: [{ lang: 1, tag: 'タグ名', slug: 'tag-slug' }]
		}
	}}
/>
