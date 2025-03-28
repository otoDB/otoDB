<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import client from '$lib/api';
	import type { components } from '$lib/schema';
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
			Accept
		</label>

		<label>
			<input type="radio" value="reject" bind:group={menu} />
			Reject
		</label>
		<div>
			{#if menu === 'new'}
				<form onsubmit={accept}>
					Attaching to...
					<table>
						<thead>
							<tr><th></th><th>Work</th></tr>
						</thead><tbody>
							{#each suggestions as work}
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
								<td>New work</td>
							</tr>
						</tbody>
					</table>
					<input type="submit" />
				</form>
			{:else}
				<form onsubmit={reject}>
					<label>Reason: <input type="text" bind:value={reason} required /></label>
					<input type="submit" />
				</form>
			{/if}
		</div>
	</div>
{:else}
	<h4><a href={null} onclick={unfold}>&gt; Actions</a></h4>
{/if}
