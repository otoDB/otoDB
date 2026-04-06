<script lang="ts">
	import { goto } from '$app/navigation';
	import client from './api';
	import { SongRelationPredicate, WorkRelationEditorPredicate } from './enums';
	import { m } from './paraglide/messages';
	import { dirtyEnhance } from './ui';
	import { getLocale } from './paraglide/runtime';
	import type { components } from './schema';
	import SongField from './SongField.svelte';
	import WorkCard from './WorkCard.svelte';
	import WorkField from './WorkField.svelte';
	import { callErrorToast } from './toast';
	import { isSOV } from './Languages';

	interface Props {
		this_id: number;
		obj_type: 'work' | 'song';
		init_relations: [components['schemas']['RelationSchema'][], { id: number }[]];
		form_control?: {
			barrier: {
				forms?: HTMLFormElement[];
				reached?: ReturnType<typeof Promise.withResolvers<void>>[];
			};
			priority: number;
		};
	}

	let { this_id, init_relations, obj_type, form_control }: Props = $props();

	let relations: { swapped: boolean; item: any | null; relation: number }[] = $state(
		init_relations[0]
			.filter(({ A_id, B_id }) => A_id === this_id || B_id === this_id)
			.map(({ A_id, B_id, relation }) => ({
				swapped: A_id === this_id,
				item: init_relations[1].find((e) => e.id === (A_id === this_id ? B_id : A_id)),
				relation
			}))
	);

	let new_item = $state(null);
	const add_new_item = async (e) => {
		if (
			new_item &&
			new_item.id !== this_id &&
			!relations.some((r) => r.item.id === new_item.id)
		) {
			e.target.dispatchEvent(new Event('change', { bubbles: true }));
			relations.unshift({ swapped: false, item: new_item, relation: 0 });
			new_item = null;
		}
	};

	const endpoint = obj_type === 'work' ? '/api/work/relation' : '/api/tag/song_relation';
	const post_gate = { p: Promise.withResolvers<void>() };
	const post_relations = async () => {
		await post_gate.p.promise;
		const { error } = await client.POST(endpoint, {
			fetch,
			params: { query: { this_id } },
			body: relations.map((r) => ({
				A_id: !r.swapped ? r.item.id : this_id!,
				B_id: r.swapped ? r.item.id : this_id!,
				relation: r.relation
			}))
		});
		if (error) {
			post_gate.p = Promise.withResolvers<void>();
			callErrorToast(m.green_due_javelina_pop());
		} else goto(`/${obj_type}/${this_id}`, { invalidateAll: true });
	};
</script>

{#snippet work(relation, swapped: boolean)}
	{#if swapped}
		{#if obj_type === 'work'}
			<WorkCard work={relation.item} />
		{:else if obj_type === 'song'}
			<a href="/tag/{relation.item.work_tag}">{relation.item.title}</a>
		{/if}
	{:else}
		{m.stout_frail_warbler_support()}{m.great_clean_beaver_amuse()}{#if obj_type === 'work'}{m.grand_merry_fly_succeed()}{:else if obj_type === 'song'}{m.grand_nice_pony_belong()}{/if}
	{/if}
{/snippet}

<form
	method="POST"
	onsubmit={post_relations}
	use:dirtyEnhance={{ ...form_control, manual_post: post_gate }}
>
	<input type="submit" class="float-right" />
	<div class="grid w-fit grid-cols-2 gap-3">
		{#if obj_type === 'work'}
			<WorkField bind:value={new_item} />
		{:else if obj_type === 'song'}
			<SongField bind:value={new_item} />
		{/if}
		<button onclick={add_new_item} type="button" disabled={!new_item}
			>{m.swift_dry_gecko_boost()}</button
		>
	</div>
	<table>
		<tbody>
			{#each relations as relation, i (i)}
				<tr>
					<td class="w-64">{@render work(relation, !relation.swapped)}</td>
					{#if isSOV(getLocale())}
						<td>{m.grand_vexed_snail_ripple()}</td>
						<td class="w-64">{@render work(relation, relation.swapped)}</td>
						<td
							><select name="relation" bind:value={relation.relation}>
								{#each obj_type === 'work' ? WorkRelationEditorPredicate : SongRelationPredicate as rel, j (j)}
									<option value={j}>{rel()}</option>
								{/each}
							</select></td
						>
					{:else}
						<td
							><select name="relation" bind:value={relation.relation}>
								{#each obj_type === 'work' ? WorkRelationEditorPredicate : SongRelationPredicate as rel, j (j)}
									<option value={j}>{rel()}</option>
								{/each}
							</select></td
						>
						<td class="w-64">{@render work(relation, relation.swapped)}</td>
					{/if}
					<td
						><button
							type="button"
							onclick={(e) => {
								e.target.dispatchEvent(new Event('change', { bubbles: true }));
								relations[i].swapped = !relations[i].swapped;
							}}>{m.less_green_angelfish_hunt()}</button
						></td
					>
					<td
						><button
							type="button"
							onclick={(e) => {
								e.target.dispatchEvent(new Event('change', { bubbles: true }));
								relations.splice(i, 1);
							}}>{m.even_alert_grebe_taste()}</button
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</form>
