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
	class={[
		'rounded-full border-2 border-solid px-2 underline',
		[
			'border-gray-300', // GENERAL
			'border-cyan-600', // EVENT
			'border-fuchsia-400', // SONG
			'border-lime-600', // SOURCE
			'border-red-600', // CREATOR
			'border-amber-400' // META
		][tag.category]
	]}>{tag.lang_prefs.find(({ lang }) => lang === Languages[getLocale()])?.tag ?? tag.name}</a
>

<style>
	a {
		text-decoration: none;
	}
</style>
