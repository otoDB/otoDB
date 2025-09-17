<script lang="ts">
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagSongSchema'];
	}
	const { tag }: Props = $props();
</script>

<a
	href="/song_attribute/{tag.slug}"
	class="rounded-xl border border-solid px-2 no-underline {[
		'border-gray-300',
		'border-indigo-600',
		'border-orange-600',
		'border-yellow-600',
		'border-red-600'
	][tag.category]}">{tag.name}</a
>
