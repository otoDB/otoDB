<script lang="ts">
	import { getTagDisplayName } from './api';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
	}
	const { tag }: Props = $props();
</script>

<a
	href="/tag/{tag.slug}"
	class="rounded-full border-2 border-solid px-2 {[
		'border-gray-300', // GENERAL
		'border-cyan-600', // EVENT
		'border-fuchsia-400', // SONG
		'border-lime-600', // SOURCE
		'border-red-600', // CREATOR
		'border-amber-400', // META
		'border-fuchsia-900' // MEDIA
	][tag.category]}">{getTagDisplayName(tag)}</a
>

<style>
	a {
		text-decoration: none;
	}
</style>
