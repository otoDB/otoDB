<script lang="ts">
	import { getTagDisplayName } from './api';
	import { WorkTagCategoriesSettableAsSource, WorkTagPresentationColours } from './enums';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
	}
	const { tag }: Props = $props();

	let overrideToSample = WorkTagCategoriesSettableAsSource.includes(tag.category) && tag?.sample;
</script>

<a
	href="/tag/{tag.slug}"
	class="rounded-xl border-2 border-solid px-2"
	style="border-color: var(--color-{WorkTagPresentationColours[
		overrideToSample ? 3 : tag.category
	]});">{getTagDisplayName(tag)}</a
>

<style>
	a {
		text-decoration: none;
	}
</style>
