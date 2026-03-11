<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Route } from '$lib/enums';
	import { timeAgo } from '$lib/ui';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';

	let { data }: PageProps = $props();
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if data.revisions?.items.length}
		<table class="w-full">
			<tbody>
				{#each data.revisions?.items as r, i (i)}
					<tr
						><td><a href="/revision/{r.id}">#{r.id}</a></td><td
							>{r.route !== null && r.route !== undefined ? Route[r.route] : ''}</td
						><td
							><time title={new Date(r.date).toLocaleString()}>{timeAgo(r.date)}</time
							></td
						></tr
					>
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
			base_url={page.url}
		/>
	{/if}
</Section>
