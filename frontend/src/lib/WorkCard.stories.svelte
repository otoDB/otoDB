<script lang="ts" module>
	import WorkCard from './WorkCard.svelte';
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import { type ComponentProps } from 'svelte';
	import thumbnail from '../stories/assets/thumbnail_1280x720.jpg';

	type WorkCardProps = ComponentProps<typeof WorkCard>;

	const { Story } = defineMeta({
		title: 'WorkCard',
		component: WorkCard
	});
</script>

<Story
	name="Primary"
	args={{
		class: 'w-64',
		work: {
			id: 1,
			title: 'Sample Work',
			thumbnail: thumbnail,
			tags: [
				{ id: 1, name: 'Tag1', slug: 'tag1', category: 0, children: [], lang_prefs: [] },
				{ id: 2, name: 'Tag2', slug: 'tag2', category: 0, children: [], lang_prefs: [] },
				{ id: 3, name: 'Tag3', slug: 'tag3', category: 0, children: [], lang_prefs: [] }
			],
			rating: 0
		}
	}}
/>

<Story
	name="No Taggings"
	args={{
		class: 'w-64',
		work: {
			id: 1,
			title: 'Sample Work',
			thumbnail: thumbnail,
			rating: 0,
			tags: []
		}
	}}
/>
