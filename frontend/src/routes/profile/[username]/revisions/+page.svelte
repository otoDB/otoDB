<script lang="ts">
	import { page } from '$app/state';
	import { routeNames } from '$lib/enums/route.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import ActionTimestamp from '$lib/ActionTimestamp.svelte';

	let { data } = $props();
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if data.revisions?.items.length}
		<table class="w-full">
			<tbody>
				{#each data.revisions?.items as r, i (i)}
					<tr>
						<td>
							<a href="/revision/{r.id}">#{r.id}</a>
						</td>
						<td>{r.route ? routeNames[r.route]() : ''}</td>
						<td>
							<ActionTimestamp date={r.date} />
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p>{m.spry_dizzy_mouse_roam()}</p>
	{/if}
	{#if data.revisions?.count}
		<Pager
			n_count={data.revisions.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>
