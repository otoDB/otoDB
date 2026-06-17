<script lang="ts" generics="T extends 'work' | 'song'">
	import { goto } from '$app/navigation';
	import { dirtyEnhance, type Control } from '$lib/dirty';
	import { isSOV } from '$lib/enums/language';
	import type { ComponentProps } from 'svelte';
	import client from '$lib/api';
	import { enumValues, SongRelationPredicate, WorkRelationEditorPredicate } from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { SongRelationTypes, WorkRelationTypes, type components } from '$lib/schema';
	import SongField from '$lib/SongField.svelte';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkField from '$lib/WorkField.svelte';

	interface Props {
		this_id: string;
		obj_type: T;
		init_relations: [
			T extends 'work'
				? components['schemas']['WorkRelationSchema'][]
				: components['schemas']['SongRelationSchema'][],
			{ id: string }[]
		];
		form_control: Control;
	}

	let { this_id, init_relations, obj_type, form_control }: Props = $props();

	type Work = components['schemas']['ThinWorkSchema'];
	type Song = components['schemas']['SongSchema'];

	let relations: {
		selected: boolean;
		tr: HTMLTableRowElement | null;
		swapped: boolean;
		item: Work | Song;
		relation: number;
	}[] = $state(
		init_relations[0]
			.filter(({ A_id, B_id }) => A_id === this_id || B_id === this_id)
			.map(({ A_id, B_id, relation }) => ({
				selected: false,
				tr: null,
				swapped: A_id === this_id,
				item: init_relations[1].find((e) => e.id === (A_id === this_id ? B_id : A_id)) as
					| Work
					| Song,
				relation
			}))
	);

	let new_item: null | Work | Song = $state(null);

	let last_clicked_index: number | null = $state(null);
	let last_entered_index: number | null = $state(null);
	let last_lo = $derived(
		last_clicked_index !== null ? Math.min(last_clicked_index, last_entered_index!) : null
	);
	let last_hi = $derived(
		last_clicked_index !== null ? Math.max(last_clicked_index, last_entered_index!) : null
	);

	const any_selected = $derived(relations.some((r) => r.selected));
	const all_selected = $derived(relations.length > 0 && relations.every((r) => r.selected));
	const uniform_relation = $derived.by(() => {
		const selected = relations.filter((r) => r.selected);
		if (selected.length === 0) return null;
		const first = selected[0].relation;
		if (!selected.every((r) => r.relation === first)) return null;
		return enumValues(RelationType).find((r) => r === first) ?? null;
	});

	const endpoint = $derived(obj_type === 'work' ? '/api/work/relation' : '/api/tag/song_relation');

	const RelationType = $derived(obj_type === 'work' ? WorkRelationTypes : SongRelationTypes);
	const Predicates = $derived(
		obj_type === 'work' ? WorkRelationEditorPredicate : SongRelationPredicate
	);
</script>

{#snippet work(
	relation: {
		item: ComponentProps<typeof WorkCard>['work'] | { work_tag: string; title: string };
	},
	swapped: boolean
)}
	{#if swapped}
		{#if obj_type === 'work'}
			<WorkCard work={relation.item as Work} />
		{:else if obj_type === 'song'}
			<a href="/tag/{(relation.item as Song).work_tag}">{relation.item.title}</a>
		{/if}
	{:else}
		{m.stout_frail_warbler_support()}{m.great_clean_beaver_amuse()}{#if obj_type === 'work'}{m.grand_merry_fly_succeed()}{:else if obj_type === 'song'}{m.grand_nice_pony_belong()}{/if}
	{/if}
{/snippet}

<svelte:window
	onmousemove={(e) => {
		if (e.buttons !== 1 || last_clicked_index === null) return;
		last_entered_index = relations
			.map((el) => el.tr!.getBoundingClientRect().top)
			.findIndex(
				(top, i, arr) => top <= e.clientY && (i + 1 === arr.length || e.clientY < arr[i + 1])
			);
	}}
	onmouseup={() => {
		if (last_clicked_index !== null)
			for (let i = last_lo!; i <= last_hi!; i++)
				relations[i].selected = relations[last_clicked_index].selected;
		last_entered_index = last_clicked_index = null;
	}}
/>

<form
	method="POST"
	use:dirtyEnhance={{
		...form_control,
		custom_submit: async ({ cancel }) => {
			cancel();
			const { error } = await client.POST(endpoint, {
				fetch,
				params: { query: { this_id } },
				body: relations.map((r) => ({
					A_id: !r.swapped ? r.item.id : this_id!,
					B_id: r.swapped ? r.item.id : this_id!,
					relation: r.relation
				}))
			});
			if (error) throw error;
			await goto(`/${obj_type}/${this_id}`, { invalidateAll: true });
		}
	}}
>
	<input type="submit" class="float-right" />
	<div class="grid w-fit grid-cols-2 gap-3">
		{#if obj_type === 'work'}
			<WorkField bind:value={new_item as Work} />
		{:else if obj_type === 'song'}
			<SongField bind:value={new_item as Song} />
		{/if}
		<button
			onclick={(e) => {
				if (
					new_item &&
					new_item.id !== this_id &&
					!relations.some((r) => r.item.id === new_item!.id)
				) {
					e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
					relations.unshift({
						selected: false,
						tr: null,
						swapped: false,
						item: new_item,
						relation: 0
					});
					new_item = null;
				}
			}}
			type="button"
			disabled={!new_item}>{m.swift_dry_gecko_boost()}</button
		>
	</div>
	{#snippet batch_select()}
		<select
			disabled={!any_selected}
			value={uniform_relation ?? ''}
			onchange={(e) => {
				const v = e.currentTarget.value;
				if (v === '') return;
				const num = Number(v);
				relations.forEach((r) => {
					if (r.selected) r.relation = num;
				});
			}}
		>
			{#if uniform_relation === null}
				<option value="" disabled={any_selected}
					>{any_selected ? m.mild_bold_finch_mix() : '---'}</option
				>
			{/if}
			{#each enumValues(RelationType) as rel, j (j)}
				<option value={rel}>{Predicates[rel]()}</option>
			{/each}
		</select>
	{/snippet}
	<table>
		{#if relations.length > 0}
			<thead>
				<tr>
					<th
						><input
							type="checkbox"
							checked={all_selected}
							indeterminate={!all_selected && any_selected}
							onchange={(e) => {
								e.stopPropagation();
								const v = e.currentTarget.checked;
								relations.forEach((r) => (r.selected = v));
							}}
						/></th
					>
					<th></th>
					{#if isSOV(getLocale())}
						<th></th>
						<th></th>
						<th>{@render batch_select()}</th>
					{:else}
						<th>{@render batch_select()}</th>
						<th></th>
					{/if}
					<th
						><button
							type="button"
							disabled={!any_selected}
							onclick={(e) => {
								e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
								relations.forEach((r) => {
									if (r.selected) r.swapped = !r.swapped;
								});
							}}>{m.less_green_angelfish_hunt()}</button
						></th
					>
					<th
						><button
							type="button"
							disabled={!any_selected}
							onclick={(e) => {
								e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
								relations = relations.filter((r) => !r.selected);
							}}>{m.even_alert_grebe_taste()}</button
						></th
					>
				</tr>
			</thead>
		{/if}
		<tbody>
			{#each relations as relation, i (i)}
				<tr bind:this={relation.tr}>
					<td
						onmousedown={(e) => {
							if (e.button !== 0) return;
							e.preventDefault();
							if (e.shiftKey) {
								const lo = relations.findIndex((r) => r.selected);
								const hi = relations.findLastIndex((r) => r.selected);
								if (lo !== -1 && hi !== -1) {
									if (i < lo) for (let k = i; k < lo; k++) relations[k].selected = true;
									else if (i > hi) for (let k = hi + 1; k <= i; k++) relations[k].selected = true;
									else relation.selected = !relation.selected;
								}
							} else {
								relation.selected = !relation.selected;
							}
							last_entered_index = last_clicked_index = i;
						}}
						><input
							type="checkbox"
							checked={last_clicked_index !== null && last_lo! <= i && i <= last_hi!
								? relations[last_clicked_index].selected
								: relation.selected}
							onclick={(e) => e.preventDefault()}
							onkeydown={(e) => {
								if (e.key === ' ') {
									e.preventDefault();
									relation.selected = !relation.selected;
								}
							}}
						/></td
					>
					<td class="w-64">{@render work(relation, !relation.swapped)}</td>
					{#if isSOV(getLocale())}
						<td>{m.grand_vexed_snail_ripple()}</td>
						<td class="w-64">{@render work(relation, relation.swapped)}</td>
						<td
							><select name="relation" bind:value={relation.relation}>
								{#each enumValues(RelationType) as rel, j (j)}
									<option value={rel}>{Predicates[rel]()}</option>
								{/each}
							</select></td
						>
					{:else}
						<td
							><select name="relation" bind:value={relation.relation}>
								{#each enumValues(RelationType) as rel, j (j)}
									<option value={rel}>{Predicates[rel]()}</option>
								{/each}
							</select></td
						>
						<td class="w-64">{@render work(relation, relation.swapped)}</td>
					{/if}
					<td
						><button
							type="button"
							onclick={(e) => {
								e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
								relations[i].swapped = !relations[i].swapped;
							}}>{m.less_green_angelfish_hunt()}</button
						></td
					>
					<td
						><button
							type="button"
							onclick={(e) => {
								e.currentTarget.dispatchEvent(new Event('change', { bubbles: true }));
								relations.splice(i, 1);
							}}>{m.even_alert_grebe_taste()}</button
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</form>

<style>
	th {
		font-weight: normal;
	}

	tbody > tr:has(input[type='checkbox']:checked) {
		background-color: color-mix(
			in hsl,
			var(--otodb-color-bg-faint) 60%,
			var(--otodb-color-content-fainter)
		);

		&:hover {
			background-color: color-mix(
				in hsl,
				var(--otodb-color-bg-faint) 40%,
				var(--otodb-color-content-fainter)
			);
		}
	}
</style>
