<script lang="ts">
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagSongSchema'];
	}
	const { tag }: Props = $props();
</script>

<a
	href="/tag/song/{tag.slug}"
	class="rounded-xl border border-solid px-2 {[
		'border-white-600',
		'border-indigo-600',
		'border-orange-600',
		'border-yellow-600',
		'border-red-600'
	][tag.category]}">{tag.name}</a
>

<style>
</style>
