<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import type { components } from '$lib/schema';
	import { isSOV, isSVO } from '$lib/ui';
	import WorkCard from '$lib/WorkCard.svelte';

	let { source } = $props();
	let opened = $state(false);
	let suggestions: components['schemas']['WorkSchema'][] = $state([]);

	const unfold = async () => {
		opened = true;
		const { data: similar } = await client.GET('/api/work/search', {
			fetch,
			params: { query: { query: source.title } }
		});
		if (similar) suggestions = similar.items;
	};

	let reason = $state(''),
		menu = $state('new'),
		candidate = $state(-1);
	const accept = async (e: SubmitEvent) => {
			e.preventDefault();
			const { error, data: w } = await client.POST('/api/work/assign_source', {
				fetch,
				params: { query: { source_id: source.id, work_id: candidate } }
			});
			if (w) goto(`/work/${w}`, { invalidateAll: true });
		},
		reject = async (e: SubmitEvent) => {
			e.preventDefault();
			const { error } = await client.POST('/api/work/reject_source', {
				fetch,
				params: { query: { source_id: source.id, reason: reason } }
			});
			invalidateAll();
		};
</script>

{#if opened}
	<div>
		<label>
			<input type="radio" value="new" bind:group={menu} />
			{m.lucky_bold_hornet_push()}
		</label>

		<label>
			<input type="radio" value="reject" bind:group={menu} />
			{m.alive_blue_marlin_push()}
		</label>
		<div>
			{#if menu === 'new'}
				<form onsubmit={accept}>
					{#if isSVO(getLocale())}
					{m.cute_neat_gull_greet()}
					{/if}
					<table>
						<thead>
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
						</tbody>
					</table>
					{#if isSOV(getLocale())}
					{m.cute_neat_gull_greet()}
					{/if}
					<input type="submit" class="block" />
				</form>
			{:else}
				<form onsubmit={reject}>
					<label
						>{m.weary_spicy_fly_attend()}
						<input type="text" bind:value={reason} required /></label
					>
					<input type="submit" />
				</form>
			{/if}
		</div>
	</div>
{:else}
	<h4><a href={null} onclick={unfold}>&gt; {m.awake_patient_fireant_pout()}</a></h4>
{/if}
