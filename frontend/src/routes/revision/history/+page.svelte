<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { isSOV, isSVO } from '$lib/ui';
	import { getLocale } from '$lib/paraglide/runtime';
	import { Route } from '$lib/enums';

	let { data }: PageProps = $props();
</script>

<Section title={m.giant_away_scallop_hike()}>
	<table class="w-full">
		<tbody>
			{#each data.results?.items as r, i (i)}
				<tr
					><td><a href="/revision/{r.id}">#{r.id}</a></td><td
						>{r.route !== null && r.route !== undefined ? Route[r.route] : ''}</td
					><td>
						{#if isSVO(getLocale())}
							{m.curly_safe_lynx_fond()}
						{/if}
						<a href="/profile/{r.user}">{r.user}</a>
						{#if isSOV(getLocale())}
							{m.curly_safe_lynx_fond()}
						{/if}</td
					><td>{new Date(r.date).toLocaleString()}</td></tr
				>
			{/each}
		</tbody>
	</table>
	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url}
		/>
	{/if}
</Section>
