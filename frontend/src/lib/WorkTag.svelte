<script lang="ts">
	import { getTagDisplayName } from './api';
	import { Role, WorkTagCategoriesSettableAsSource, WorkTagPresentationColours } from './enums';
	import type { components } from './schema';

	interface Props {
		tag: components['schemas']['TagWorkSchema'];
		tree: boolean | undefined;
	}
	const { tag, tree = false }: Props = $props();

	let overrideToSample = (tag) =>
		WorkTagCategoriesSettableAsSource.includes(tag.category) && tag?.sample;
</script>

{#snippet render_tag(t, border = true, sample_override = false, fade_out = false)}
	<a
		href="/tag/{t.slug}"
		class={[
			'rounded-xl border-solid px-2',
			border ? 'border-2' : 'border-1',
			{ 'opacity-50': fade_out }
		]}
		style="border-color: {WorkTagPresentationColours[sample_override ? 3 : t.category]};"
		>{getTagDisplayName(t)}</a
	>{#if t.category === 4 && t.creator_roles?.length}<address
			class="text-otodb-content-fainter inline px-1 text-xs"
		>
			{#each t.creator_roles as role, i (i)}{Role[
					role
				]()}{#if i < t.creator_roles.length - 1},&nbsp{/if}{/each}
		</address>{/if}
{/snippet}

{#snippet recur(this_snippet, tree)}
	<ul class="my-0.5 list-none">
		<li class="inline">
			{@render render_tag(tree.node, false, overrideToSample(tree.node), !tree.real)}
		</li>
		{#if tree.children?.length}
			{#each tree.children as t, i (i)}
				<li>
					{@render this_snippet(this_snippet, t)}
				</li>
			{/each}
		{/if}
	</ul>
{/snippet}

{#if tree}
	{@render recur(recur, tag)}
{:else}
	{@render render_tag(tag, true, overrideToSample(tag))}
{/if}

<style>
	a {
		text-decoration: none;
	}
	ul > li > ul {
		&::before {
			content: '\21B3';
		}
		& > li > ul {
			margin-left: 0.5rem;
		}
	}
</style>
