<script lang="ts">
	import TagsField from '$lib/TagsField.svelte';
	import TagEditTable from '$lib/TagEditTable.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory';
	import { m } from '$lib/paraglide/messages';
	import { getTagDisplaySlug } from '$lib/ui.js';
	import type { components } from '$lib/schema.js';
	import type { ComponentProps } from 'svelte';

	interface Props {
		tags: string[];
		cache: Record<string, components['schemas']['TagWorkInstanceThinSchema']>;
		suggestions?: components['schemas']['SourceSuggestionsResponse'] | null;
	}

	let { tags = $bindable([]), cache = $bindable({}), suggestions = null }: Props = $props();

	const sortedSuggestions = $derived(
		[
			...(suggestions?.source_tags ?? []),
			...(suggestions?.creator_tags ?? []),
			...(suggestions?.new_tags ?? [])
		].sort(
			(a, b) =>
				WorkTagCategoryMap[a.category].order - WorkTagCategoryMap[b.category].order ||
				a.name.localeCompare(b.name)
		)
	);

	$effect(() => {
		for (const t of sortedSuggestions) {
			const slug = getTagDisplaySlug(t);
			if (!cache[slug]) {
				cache[slug] = { ...t, sample: false, creator_roles: null };
			}
		}
	});

	const toggleTag: ComponentProps<typeof WorkTag>['onclick'] = (tag) => {
		const slug = getTagDisplaySlug(tag);
		if (tags.includes(slug)) {
			tags = tags.filter((t) => t !== slug);
		} else {
			tags = [...tags, slug];
		}
	};
</script>

{#if sortedSuggestions.length}
	<div class="text-otodb-content-fainter my-1 text-sm">{m.keen_mild_lark_point()}</div>
	<div class="my-2 flex flex-wrap gap-1.5">
		{#each sortedSuggestions as t (t.slug)}
			<WorkTag tag={t} selected={tags.includes(getTagDisplaySlug(t))} onclick={toggleTag} />
		{/each}
	</div>
{/if}
<TagsField type="work" class="w-full" bind:value={tags} />
<TagEditTable {tags} bind:cache />
