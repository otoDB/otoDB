<script lang="ts">
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import type { components } from '$lib/schema';
	import { isSOV, isSVO } from '$lib/ui';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkField from '$lib/WorkField.svelte';

	let { source } = $props();
	let suggestions: components['schemas']['WorkSchema'][] = $state([]);
	let specify_target: components['schemas']['WorkSchema'] | null = $state(null);

	let loaded = false;
	const unfold = async () => {
		if (!loaded && menu === 'new') {
			const { data: similar } = await client.GET('/api/work/search', {
				fetch,
				params: { query: { query: source.title } }
			});
			if (similar) suggestions = similar.items;
			loaded = true;
		}
	};

	let reason = $state(''),
		menu: 'none' | 'new' | 'reject' = $state('none'),
		candidate = $state(-1);
	export async function submit() {
		if (menu === 'new')
			await client.POST('/api/work/assign_source', {
				fetch,
				params: {
					query: {
						source_id: source.id,
						work_id:
							candidate === -1
								? undefined
								: candidate === 0
									? specify_target?.id
									: candidate
					}
				}
			});
		else if (menu === 'reject')
			await client.POST('/api/work/reject_source', {
				fetch,
				params: { query: { source_id: source.id, reason: reason } }
			});
	};
</script>

<td>
	<label>
		<input autocomplete="off" type="radio" value="none" bind:group={menu} />
		No action
	</label>
</td>

<td>
	<label>
		<input autocomplete="off" type="radio" value="new" bind:group={menu} onchange={unfold} />
		{m.lucky_bold_hornet_push()}
	</label>
	{#if menu === 'new'}
		{#if isSVO(getLocale())}
			{m.cute_neat_gull_greet()}
		{/if}
		<table><thead>
				<tr><th></th><th>{m.grand_merry_fly_succeed()}</th></tr>
			</thead><tbody>
				{#each suggestions as work, i (i)}
					<tr>
						<td
							><input
								type="radio"
								value={work.id}
								bind:group={candidate}
							/></td
						>
						<td><WorkCard {work} /></td>
					</tr>
				{/each}
				<tr>
					<td><input type="radio" value={-1} bind:group={candidate} /></td>
					<td>{m.careful_red_cow_evoke()}</td>
				</tr>
				<tr>
				<td><input type="radio" value={0} bind:group={candidate} /></td>
				<td>
					<WorkField value={specify_target} />
				</td>
			</tr>
		</tbody></table>
		{#if isSOV(getLocale())}
			{m.cute_neat_gull_greet()}
		{/if}
	{/if}
</td>
<td>
	<label>
		<input autocomplete="off" type="radio" value="reject" bind:group={menu} />
		{m.alive_blue_marlin_push()}
	</label>
	{#if menu === 'reject'}
	<label
		>{m.weary_spicy_fly_attend()}
		<input type="text" bind:value={reason} required /></label
	>
	{/if}
</td>
<!-- <a href={null} onclick={unfold}> -->