<script lang="ts">
	import WorkTag from '$lib/WorkTag.svelte';
	import { getTagDisplaySlug } from '$lib/api';
	import { Role, WorkTagCategoriesSettableAsSource } from '$lib/enums';
	import { m } from '$lib/paraglide/messages.js';
	import type { components } from '$lib/schema.js';

	type TagCache = Record<string, components['schemas']['TagWorkInstanceThinSchema']>;

	let {
		tags,
		cache,
		ontoggle_sample,
		ontoggle_creator_role
	}: {
		tags: string[];
		cache: TagCache;
		ontoggle_sample: (slug: string) => void;
		ontoggle_creator_role: (slug: string, role_value: number) => void;
	} = $props();
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
								onclick={() => ontoggle_sample(getTagDisplaySlug(tag))}
								checked={tag.sample}
							/>
						{:else}{m.simple_less_marlin_enchant()}{/if}
					</td>
					<td>
						{#if tag.category === 4}
							{#each Object.keys(Role).filter((e) => !isNaN(+e)) as k, i (i)}
								<label class="role-label">
									<input
										class="hidden"
										type="checkbox"
										checked={tag.creator_roles?.includes(+k) || false}
										onchange={() =>
											ontoggle_creator_role(getTagDisplaySlug(tag), +k)}
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
