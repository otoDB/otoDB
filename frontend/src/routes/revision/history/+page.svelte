<script lang="ts">
	import { page } from '$app/state';
	import Pager from '$lib/Pager.svelte';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import { isSOV, isSVO } from '$lib/enums/language.js';
	import { routeNames } from '$lib/enums/route.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';

	let { data } = $props();
</script>

<Section title={m.giant_away_scallop_hike()}>
	<table class="w-full">
		<tbody>
			{#each data.results?.items as r, i (i)}
				<tr
					><td><a href="/revision/{r.id}">#{r.id}</a></td><td
						>{r.route ? routeNames[r.route]() : ''}</td
					><td>
						{#if isSVO(getLocale())}
							{m.curly_safe_lynx_fond()}
						{/if}
						<a href="/profile/{r.user}">{r.user}</a>
						{#if isSOV(getLocale())}
							{m.curly_safe_lynx_fond()}
						{/if}</td
					><td><Time format="relative" date={r.date} /></td></tr
				>
			{/each}
		</tbody>
	</table>
	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page={data.page}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>
