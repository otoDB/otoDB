<script lang="ts">
	import { goto } from '$app/navigation';
	import client, { getTagDisplaySlug } from '$lib/api.js';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import TagEditTable from '$lib/TagEditTable.svelte';
	import GuidelineWarning from '$lib/GuidelineWarning.svelte';
	import type { components } from '$lib/schema.js';

	let { data } = $props();

	let tags: string[] = $derived(data.tags.map((t) => getTagDisplaySlug(t)));
	let cache: Record<string, components['schemas']['TagWorkInstanceThinSchema']> = $state(
		Object.fromEntries(data.tags.map((t) => [getTagDisplaySlug(t), t]))
	);

	$effect(() => {
		void tags;
		const timeout = setTimeout(() => {
			tags.filter((t) => !Object.hasOwn(cache, t)).forEach(async (t) => {
				let result = await client.GET('/api/tag/tag', {
					fetch,
					params: { query: { tag_slug: t } }
				});
				if (result.response.status === 300 && typeof result.error === 'string') {
					result = await client.GET('/api/tag/tag', {
						fetch,
						params: { query: { tag_slug: result.error } }
					});
				}
				cache[t] = result.data ?? {
					aliased_to: null,
					category: 0,
					creator_roles: null,
					deprecated: false,
					id: -1,
					lang_prefs: [],
					name: t,
					sample: false,
					slug: t
				};
			});
		}, 750);

		return () => clearTimeout(timeout);
	});

	const toggle_creator_role = (tag_slug: string, role_value: number) => {
		const tag = cache[tag_slug];
		const current_roles = tag.creator_roles || [];
		const new_roles = current_roles.includes(role_value)
			? current_roles.filter((r: number) => r !== role_value)
			: [...current_roles, role_value];
		tag.creator_roles = new_roles;
	};

	const toggle_sample = (tag_slug: string) => {
		cache[tag_slug].sample = !cache[tag_slug].sample;
	};

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
		<div><TagsField type="work" class="w-full" bind:value={tags} /></div>
		<TagEditTable
			{tags}
			{cache}
			ontoggle_sample={toggle_sample}
			ontoggle_creator_role={toggle_creator_role}
		/>
		<input type="submit" />
	</form>
</Section>
