<script lang="ts">
	import { goto } from '$app/navigation';
	import { dirtyEnhance, type Barrier } from '$lib/dirty';
	import { isSOV } from '$lib/enums/Languages';
	import type { ComponentProps } from 'svelte';
	import client from './api';
	import { SongRelationPredicate, WorkRelationEditorPredicate } from './enums';
	import { m } from './paraglide/messages';
	import { getLocale } from './paraglide/runtime';
	import type { components } from './schema';
	import SongField from './SongField.svelte';
	import { callErrorToast } from './toast';
	import WorkCard from './WorkCard.svelte';
	import WorkField from './WorkField.svelte';

	interface Props {
		this_id: number;
		obj_type: 'work' | 'song';
		init_relations: [components['schemas']['RelationSchema'][], { id: number }[]];
		form_control?: {
			barrier: Partial<Barrier>;
			priority: number;
		};
	}

	let { this_id, init_relations, obj_type, form_control }: Props = $props();

	type WorkTag = ComponentProps<typeof WorkCard>['work'];
	type SongTag = { work_tag: string; title: string; id: number };

	let relations: { swapped: boolean; item: WorkTag | SongTag; relation: number }[] = $state(
		init_relations[0]
			.filter(({ A_id, B_id }) => A_id === this_id || B_id === this_id)
			.map(({ A_id, B_id, relation }) => ({
				swapped: A_id === this_id,
				item: init_relations[1].find((e) => e.id === (A_id === this_id ? B_id : A_id))! as
					| WorkTag
					| SongTag,
				relation
			}))
	);

	let new_item: null | WorkTag | SongTag = $state(null);

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

{#snippet work(
	relation: {
		item: ComponentProps<typeof WorkCard>['work'] | { work_tag: string; title: string };
	},
	swapped: boolean
)}
	{#if swapped}
		{#if obj_type === 'work'}
			<WorkCard work={relation.item as WorkTag} />
		{:else if obj_type === 'song'}
			<a href="/tag/{(relation.item as SongTag).work_tag}">{relation.item.title}</a>
		{/if}
	{:else}
		{m.stout_frail_warbler_support()}{m.great_clean_beaver_amuse()}{#if obj_type === 'work'}{m.grand_merry_fly_succeed()}{:else if obj_type === 'song'}{m.grand_nice_pony_belong()}{/if}
	{/if}
{/snippet}

<form
	method="POST"
	onsubmit={post_relations}
	// @ts-expect-error I gave up on typing this
	use:dirtyEnhance={{ ...form_control, manual_post: post_gate }}
>
	<input type="submit" class="float-right" />
	<div class="grid w-fit grid-cols-2 gap-3">
		{#if obj_type === 'work'}
			<WorkField
				// @ts-expect-error I gave up on typing this
				bind:value={new_item}
			/>
		{:else if obj_type === 'song'}
			<SongField
				// @ts-expect-error I gave up on typing this
				bind:value={new_item}
			/>
		{/if}
		<button
			onclick={(e) => {
				if (
					new_item &&
					new_item.id !== this_id &&
					!relations.some((r) => r.item.id === new_item!.id)
				) {
					e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
					relations.unshift({ swapped: false, item: new_item, relation: 0 });
					new_item = null;
				}
			}}
			type="button"
			disabled={!new_item}>{m.swift_dry_gecko_boost()}</button
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
								e.currentTarget.dispatchEvent(
									new Event('change', { bubbles: true })
								);
								relations[i].swapped = !relations[i].swapped;
							}}>{m.less_green_angelfish_hunt()}</button
						></td
					>
					<td
						><button
							type="button"
							onclick={(e) => {
								e.currentTarget.dispatchEvent(
									new Event('change', { bubbles: true })
								);
								relations.splice(i, 1);
							}}>{m.even_alert_grebe_taste()}</button
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</form>
