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
			tags: [...new Array(3)].map((_, i) => ({
				id: i,
				name: 'Tag ' + i,
				slug: 'tag_' + i,
				category: 0,
				children: [],
				lang_prefs: []
			})),
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
