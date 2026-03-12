<script lang="ts">
	import { goto } from '$app/navigation';
	import client, { getTagDisplaySlug } from '$lib/api.js';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import { Role, WorkTagCategoriesSettableAsSource } from '$lib/enums';
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
				const { data } = await client.GET('/api/tag/tag', {
					fetch,
					params: { query: { tag_slug: t } }
				});
				cache[t] = data ?? {
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

	const toggle_creator_role = async (tag_slug: string, role_value: number) => {
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
			body: Object.values(cache).map(t => ({nameslug: t.slug, roles: t.creator_roles, sample: t.sample}))
		});
		goto(`/work/${data.id}`, { invalidateAll: true });
	};
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<GuidelineWarning />
	<form onsubmit={submit_tags}>
		<div><TagsField type="work" class="w-full" bind:value={tags} /></div>
		<table>
			<thead>
				<tr
					><th>{m.empty_legal_chicken_taste()}</th>
					<th>{m.acidic_brave_halibut_heart()}</th>
					<th>{m.broad_wide_lemming_hint()}</th></tr
				>
			</thead><tbody>
				{#each tags as slug, i (i)}
					{#if cache[slug]}
						{@const tag = cache[slug]}
						<tr>
							<td><WorkTag {tag} /></td>
							<td
								>{#if WorkTagCategoriesSettableAsSource.includes(tag.category)}
									<input
										type="checkbox"
										onclick={() => toggle_sample(getTagDisplaySlug(tag))}
										checked={tag.sample}
									/>
								{:else}{m.simple_less_marlin_enchant()}{/if}</td
							>
							<td>
								{#if tag.category === 4}
									{#each Object.keys(Role).filter((e) => !isNaN(e)) as k, i (i)}
										<label class="role-label">
											<input
												class="hidden"
												type="checkbox"
												checked={tag.creator_roles?.includes(+k) || false}
												onchange={() =>
													toggle_creator_role(getTagDisplaySlug(tag), +k)}
											/>{Role[k]()}
										</label>
									{/each}
								{:else}
									{m.simple_less_marlin_enchant()}
								{/if}
							</td>
						</tr>
					{/if}
				{/each}
			</tbody>
		</table>
		<input type="submit" />
	</form>
</Section>

<style>
	label.role-label {
		padding: 0 0.3rem;
		margin: 0.1rem;
		border: 1px solid var(--otodb-color-content-primary);
		&:has(input:checked) {
			background-color: var(--otodb-color-content-primary);
			color: var(--color-otodb-bg-primary);
		}
		color: var(--otodb-color-content-primary);
		background-color: var(--otodb-color-bg-primary);
	}
</style>
