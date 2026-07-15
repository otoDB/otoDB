<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api.js';
	import { dirtyEnhance } from '$lib/dirty';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import TagsEditor from '$lib/TagsEditor.svelte';
	import type { components } from '$lib/schema.js';
	import { getTagDisplaySlug, getMissingCategories } from '$lib/ui.js';
	import Banner from '$lib/Banner.svelte';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';

	let { data } = $props();

	let tags: string[] = $state(data.tags.map((t) => getTagDisplaySlug(t)));
	let cache: Record<string, components['schemas']['TagWorkInstanceThinSchema']> = $state(
		Object.fromEntries(data.tags.map((t) => [getTagDisplaySlug(t), t]))
	);

	let missingCategories = $derived.by(() => getMissingCategories(Object.values(cache)));
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	{#if missingCategories.length > 0}
		<Banner variant="info">
			<div class="text-sm">
				{m.watery_kind_quail_climb({
					missing: missingCategories.map((c) => WorkTagCategoryMap[c].nameFn()).join(', ')
				})}
			</div>
		</Banner>
	{/if}
	<GuidelineWarning />
	<form
		method="POST"
		use:dirtyEnhance={{
			custom_submit: async ({ cancel }) => {
				cancel();
				await client.PUT('/api/work/set_tags', {
					fetch,
					params: { query: { work_id: data.id } },
					body: tags
						.filter((t) => cache[t])
						.map((t) => ({
							nameslug: cache[t].slug,
							roles: cache[t].creator_roles,
							sample: cache[t].sample
						}))
				});
				await goto(`/work/${data.id}`, { invalidateAll: true });
			}
		}}
	>
		<TagsEditor bind:tags bind:cache suggestions={data.suggestions} />
		<input type="submit" />
	</form>
</Section>
