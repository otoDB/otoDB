<script lang="ts">
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';

	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/ui.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import { Route } from '$lib/enums.js';

	let { data } = $props();
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta
		name="description"
		content={m.mild_loud_shad_enchant({ type: 'otoDB', name: m.glad_born_mouse_taste() })}
	/>
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<ul>
		<li><a href="/post/2">{m.noble_fine_iguana_pull()}</a></li>
		<li><a href="/post/3">FAQ</a></li>
		{#if data.user}
			<li><a href="/post/4">{m.arable_direct_cougar_win()}</a></li>
			<li><a href="/post/1">{m.bald_ideal_gadfly_jest()}</a></li>
		{/if}
	</ul>
</Section>

<div class="grid grid-cols-[repeat(auto-fill,minmax(min(100%,576px),1fr))] gap-x-4">
	<Section title={m.fuzzy_chunky_niklas_peek()}>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.random as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</Section>

	<Section title={m.big_long_squirrel_kiss()}>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.recent as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</Section>

	<Section title={m.sea_cute_beaver_file()}>
		<table class="w-full">
			<tbody>
				{#each data.changes.items as r, i (i)}
					<tr
						><td><a href="/revision/{r.id}">#{r.id}</a> </td><td
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
		<a href="/revision/history" class="float-right">{m.fresh_deft_warbler_edit()}</a>
	</Section>

	<Section title={m.curly_fuzzy_turkey_launch()}>
		<table class="w-full">
			<tbody>
				{#each data.posts.items as p, i (i)}
					<tr>
						<td><a href="/post/{p.id}">{p.title}</a></td>
						<td>{new Date(p.modified).toLocaleString()}</td>
					</tr>
				{/each}
			</tbody>
		</table>
		<a href="/post/overview" class="float-right">{m.fresh_deft_warbler_edit()}</a>
	</Section>
</div>
