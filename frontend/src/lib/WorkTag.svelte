<script lang="ts">
	import { getTagDisplayName } from './api';
	import { WorkTagCategoriesSettableAsSource, WorkTagPresentationColours } from './enums';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
		tree: boolean | undefined;
	}
	const { tag, tree = false }: Props = $props();

	let overrideToSample = WorkTagCategoriesSettableAsSource.includes(tag.category) && tag?.sample;
</script>

{#snippet render_tag(t, border = true, sample_override = false)}
	<a
		href="/tag/{t.slug}"
		class={['rounded-xl border-solid px-2', border ? 'border-2' : 'border-1']}
		style="border-color: {WorkTagPresentationColours[
			sample_override ? 3 : t.category
		]};">{getTagDisplayName(t)}</a
	>
{/snippet}

{#if tree && tag.primary_path}
	<ul class="flex list-none flex-col gap-1">
		{#each tag.primary_path as t, i (i)}
			<li
				style="margin-left: calc(max({Math.max(0, i - 1)}rem / 2);"
				class={['opacity-50', { "before:content-['↳']": i !== 0 }]}
			>
				{@render render_tag(t, false)}
			</li>
		{/each}
		<li
			class={{ "before:content-['↳']": tag.primary_path.length }}
			style="margin-left: calc({Math.max(tag.primary_path.length - 1, 0)}rem / 2);"
		>
			{@render render_tag(tag, false, overrideToSample)}
		</li>
	</ul>
{:else}
	{@render render_tag(tag, true, overrideToSample)}
{/if}

<style>
	a {
		text-decoration: none;
	}
</style>
