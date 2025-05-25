<script lang="ts">
	import { Languages } from './enums';
	import { getLocale } from './paraglide/runtime';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
	}
	const { tag }: Props = $props();
</script>

<a
	href="/tag/{tag.slug}"
	class="rounded-full border-2 border-solid px-2 {[
		'border-white-600',
		'border-indigo-600',
		'border-cyan-600',
		'border-orange-900',
		'border-yellow-400',
		'border-red-600'
	][tag.category]}"
	>{tag.lang_prefs.find(({ lang }) => lang === Languages[getLocale()])?.tag ?? tag.name}</a
>

<style>
	a {
		text-decoration: none;
	}
</style>
