<script lang="ts">
	import TagsField from '$lib/TagsField.svelte';
	import TagEditTable from '$lib/TagEditTable.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory';
	import { m } from '$lib/paraglide/messages';
	import { getTagDisplaySlug, getTagDisplayName } from '$lib/ui.js';
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

	// Known tags go by slug, which can carry a `_N` suffix the name cannot reproduce.
	// Suggested new tags (id `'0'`) have no slug yet, so they go by name.
	const tokenOf = (tag: ComponentProps<typeof WorkTag>['tag']) =>
		tag.id === '0' ? getTagDisplayName(tag).replace(/\s+/g, '_') : getTagDisplaySlug(tag);

	$effect(() => {
		for (const t of sortedSuggestions) {
			const token = tokenOf(t);
			if (!cache[token]) {
				cache[token] = { ...t, sample: false, creator_roles: null };
			}
		}
	});

	const toggleTag: ComponentProps<typeof WorkTag>['onclick'] = (tag) => {
		const token = tokenOf(tag);
		if (tags.includes(token)) {
			tags = tags.filter((t) => t !== token);
		} else {
			tags = [...tags, token];
		}
	};
</script>

{#if sortedSuggestions.length}
	<div class="text-otodb-content-fainter my-1 text-sm">{m.keen_mild_lark_point()}</div>
	<div class="my-2 flex flex-wrap gap-1.5">
		{#each sortedSuggestions as t (t.slug)}
			<WorkTag tag={t} selected={tags.includes(tokenOf(t))} onclick={toggleTag} />
		{/each}
	</div>
{/if}
<TagsField type="work" class="w-full" bind:value={tags} />
<TagEditTable {tags} bind:cache />
