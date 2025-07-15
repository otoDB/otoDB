<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api.js';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import { Role } from '$lib/enums';

	let { data } = $props();

	let tags = $state(data.tags);

	const set_score = (new_vote: number, tag) => async (e) => {
		e.preventDefault();
		await client.PUT('/api/work/tag_scores', {
			fetch,
			params: { query: { work_id: +data.id } },
			body: [{ score: new_vote, tag_slug: tag.slug }]
		});
		tag.user_score = new_vote;

		const original_tag = data.tags.find((t) => t.slug === tag.slug)!;
		if (original_tag && original_tag.user_score !== null)
			tag.score =
				original_tag.score -
				original_tag.user_score / original_tag.n_votes +
				new_vote / original_tag.n_votes;
		else {
			tag.score =
				(original_tag.score * original_tag.n_votes + new_vote) / (original_tag.n_votes + 1);
			original_tag.n_votes++;
			tag.n_votes = original_tag.n_votes;
			original_tag.user_score = new_vote;
			original_tag.score = tag.score;
		}
	};

	const toggle_creator_role = async (tag_slug: string, role_value: number) => {
		const tag = tags.find((t) => t.slug === tag_slug);
		if (!tag || tag.category !== 4) return; // Creator tags only

		const current_roles = tag.creator_roles || [];
		const new_roles = current_roles.includes(role_value)
			? current_roles.filter((r: number) => r !== role_value)
			: [...current_roles, role_value];

		const response = await client.POST('/api/work/creator_roles', {
			fetch,
			body: { work_id: +data.id, tag_slug, creator_roles: new_roles }
		});

		if (response.response.ok) {
			tag.creator_roles = new_roles;
		}
	};

	let new_tags: string[] = $state([]);
	const submit_new_tags = async (e: SubmitEvent) => {
		e.preventDefault();
		await client.PUT('/api/work/tag_scores', {
			fetch,
			params: { query: { work_id: +data.id } },
			body: new_tags.map((t) => ({ tag_slug: t, score: 1 }))
		});
		goto(`/work/${data.id}`, { invalidateAll: true });
	};

	const toggle_sample = async (tag_slug: string) => {
		await client.PUT('/api/work/toggle_sample', {
			fetch,
			params: { query: { work_id: data.id, tag_slug } }
		});
	};
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.grand_merry_fly_succeed(), name: data.title })}
	menuLinks={data.links}
>
	<table>
		<thead>
			<tr
				><th>{m.empty_legal_chicken_taste()}</th><th>{m.brave_tiny_meerkat_engage()}</th><th
					>{m.sunny_deft_puffin_scoop()}</th
				><th>{m.acidic_brave_halibut_heart()}</th>
				<th>{m.broad_wide_lemming_hint()}</th></tr
			>
		</thead><tbody>
			{#each tags as tag, i (i)}
				<tr>
					<td><WorkTag {tag} /></td>
					<td>{tag.score} {m.brave_caring_ocelot_treat({ votes: tag.n_votes })}</td>
					<td>
						<button
							class="rating"
							data-checked={tag.user_score === -1}
							onclick={set_score(-1, tag)}
							aria-label="-1"
						></button>
						<button
							class="rating"
							data-checked={tag.user_score !== null}
							onclick={set_score(0, tag)}
							aria-label="0"
						></button>
						<button
							class="rating"
							data-checked={tag.user_score === 1}
							onclick={set_score(1, tag)}
							aria-label="+1"
						></button>
					</td>
					<!-- 2 - Song, 4 - Creator -->
					<td
						>{#if tag.category === 2 || tag.category === 4}
							<input
								type="checkbox"
								onclick={() => toggle_sample(tag.slug)}
								checked={tag.sample}
							/>
						{:else}{m.simple_less_marlin_enchant()}{/if}</td
					>
					<td>
						{#if tag.category === 4}
							<div class="creator-roles">
								{#each Object.entries(Role) as [, value] (value)}
									{#if typeof value === 'number'}
										<label>
											<input
												type="checkbox"
												checked={tag.creator_roles?.includes(value) ||
													false}
												onchange={() =>
													toggle_creator_role(tag.slug, value)}
											/>
											<!-- {Role[value as keyof typeof Role]} -->
										</label>
									{/if}
								{/each}
							</div>
						{:else}
							{m.simple_less_marlin_enchant()}
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>

	<h3>{m.patient_male_ox_praise()}</h3>
	<form onsubmit={submit_new_tags}>
		<div><TagsField type="work" class="w-full" bind:value={new_tags} /></div>
		<input type="submit" />
	</form>
</Section>

<style>
	button.rating {
		background-color: var(--otodb-bg-color);
		border: 1px var(--otodb-content-color) solid;
		width: 1rem;
		height: 1rem;
		display: inline-block;
		&[data-checked='true'] {
			background-color: var(--otodb-faint-content);
		}
	}
</style>
