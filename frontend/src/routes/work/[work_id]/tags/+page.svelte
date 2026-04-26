<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api.js';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import TagsEditor from '$lib/TagsEditor.svelte';
	import type { components } from '$lib/schema.js';
	import { getTagDisplaySlug } from '$lib/ui.js';

	let { data } = $props();

	let tags: string[] = $state(data.tags.map((t) => getTagDisplaySlug(t)));
	let cache: Record<string, components['schemas']['TagWorkInstanceThinSchema']> = $state(
		Object.fromEntries(data.tags.map((t) => [getTagDisplaySlug(t), t]))
	);

	const submit_tags = async (e: SubmitEvent) => {
		e.preventDefault();
		await client.PUT('/api/work/set_tags', {
			fetch,
			params: { query: { work_id: +data.id } },
			body: tags
				.filter((t) => cache[t])
				.map((t) => ({
					nameslug: cache[t].slug,
					roles: cache[t].creator_roles,
					sample: cache[t].sample
				}))
		});
		goto(`/work/${data.id}`, { invalidateAll: true });
	};
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<GuidelineWarning />
	<form onsubmit={submit_tags}>
		<TagsEditor bind:tags bind:cache suggestions={data.suggestions} />
		<input type="submit" />
	</form>
</Section>
