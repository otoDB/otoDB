<script lang="ts">
	import { getTagDisplayName } from './api';
	import { WorkTagCategoriesSettableAsSource } from './enums';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
	}
	const { tag }: Props = $props();

	let overrideToSample = WorkTagCategoriesSettableAsSource.includes(tag.category) && tag?.sample;
</script>

<a
	href="/tag/{tag.slug}"
	class="rounded-xl border-2 border-solid px-2 {[
		'border-gray-300', // GENERAL
		'border-cyan-600', // EVENT
		'border-fuchsia-400', // SONG
		'border-lime-600', // SOURCE
		'border-red-600', // CREATOR
		'border-amber-400', // META
		'border-fuchsia-900' // MEDIA
	][overrideToSample ? 3 : tag.category]}">{getTagDisplayName(tag)}</a
>

<style>
	a {
		text-decoration: none;
	}
</style>
