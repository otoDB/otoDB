<script lang="ts">
	import WorkTag from '$lib/WorkTag.svelte';
	import { clientRaw as client, getTagDisplaySlug } from '$lib/api';
	import { WorkTagCategoriesSettableAsSource } from '$lib/enums';
	import { allCreatorRoles, creatorRole } from '$lib/enums/CreatorRole';
	import { m } from '$lib/paraglide/messages.js';
	import type { ComponentProps } from 'svelte';

	type TagCache = Record<string, ComponentProps<typeof WorkTag>['tag']>;

	let {
		tags,
		cache = $bindable()
	}: {
		tags: string[];
		cache: TagCache;
	} = $props();

	$effect(() => {
		void tags;
		const timeout = setTimeout(() => {
			tags.filter((t) => !Object.hasOwn(cache, t)).forEach(async (t) => {
				let {
					data,
					error: redirectSlug,
					response
				} = await client.GET('/api/tag/tag', {
					params: { query: { tag_slug: t } }
				});
				if (response.status === 300 && typeof redirectSlug === 'string') {
					({ data } = await client.GET('/api/tag/tag', {
						params: { query: { tag_slug: redirectSlug } }
					}));
				}
				cache[t] = data ?? {
					category: 0,
					creator_roles: null,
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

	const toggle_sample = (tag_slug: string) => {
		cache[tag_slug].sample = !cache[tag_slug].sample;
	};

	const toggle_creator_role = (tag_slug: string, role_value: number) => {
		const tag = cache[tag_slug];
		const current_roles = tag.creator_roles || [];
		const new_roles = current_roles.includes(role_value)
			? current_roles.filter((r: number) => r !== role_value)
			: [...current_roles, role_value];
		tag.creator_roles = new_roles;
	};
</script>

<table>
	<thead>
		<tr>
			<th>{m.empty_legal_chicken_taste()}</th>
			<th>{m.acidic_brave_halibut_heart()}</th>
			<th>{m.broad_wide_lemming_hint()}</th>
		</tr>
	</thead>
	<tbody>
		{#each tags as slug, i (i)}
			{#if cache[slug]}
				{@const tag = cache[slug]}
				<tr>
					<td><WorkTag {tag} /></td>
					<td>
						{#if WorkTagCategoriesSettableAsSource.includes(tag.category)}
							<input
								type="checkbox"
								onclick={() => toggle_sample(getTagDisplaySlug(tag))}
								checked={tag.sample}
							/>
						{:else}{m.simple_less_marlin_enchant()}{/if}
					</td>
					<td>
						{#if tag.category === 4}
							{#each allCreatorRoles as k (k)}
								<label class="role-label">
									<input
										class="hidden"
										type="checkbox"
										checked={tag.creator_roles?.includes(creatorRole[k].id) ||
											false}
										onchange={() =>
											toggle_creator_role(
												getTagDisplaySlug(tag),
												creatorRole[k].id
											)}
									/>{creatorRole[k].nameFn()}
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
