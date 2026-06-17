<script lang="ts">
	import { EntityModelRoutes } from '$lib/enums.js';
	import { routeNames } from '$lib/enums/route.js';
	import { m } from '$lib/paraglide/messages.js';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import WorkCard from '$lib/WorkCard.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	let { data } = $props();
</script>

<Section title={m.fine_late_chicken_quiz()}>
	<p>{m.silly_main_reindeer_chop()}</p>
	<ul>
		<li><a href="/wiki/about">{m.noble_fine_iguana_pull()}</a></li>
		<li><a href="/wiki/faq">FAQ</a></li>
		{#if data.user}
			<li><a href="/wiki/editing_guidelines">{m.arable_direct_cougar_win()}</a></li>
		{/if}
	</ul>
</Section>

<div
	class="grid grid-cols-[repeat(auto-fill,minmax(max(calc(50%-var(--spacing)*2),min(100%,576px)),1fr))] gap-x-4"
>
	<Section title={m.fuzzy_chunky_niklas_peek()} href="/work/random">
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.random as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</Section>

	<Section title={m.big_long_squirrel_kiss()} href="/work">
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.recent as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</Section>

	<Section title={m.sea_cute_beaver_file()} href="/revision">
		<table class="w-full">
			<tbody>
				{#each data.changes.items as r, i (i)}
					<tr
						><td><a href="/revision/{r.id}">#{r.id}</a> </td><td
							>{typeof r.route === 'number' ? routeNames[r.route]() : ''}</td
						><td
							>{#if r.n_ent == 1}<a
									href="{EntityModelRoutes[r.first_entity.entity]}/{r.first_entity.id}"
									>/{EntityModelRoutes[r.first_entity.entity]}/{r.first_entity.id}</a
								>{:else}{r.n_ent} Entities{/if}</td
						><td
							><Time format="relative" date={r.date} /><ParaglideMessage
								message={m.noble_tidy_boar_lock}
								inputs={{}}
								>{#snippet content()}<a href="/profile/{r.user}">{r.user}</a
									>{/snippet}</ParaglideMessage
							></td
						></tr
					>
				{/each}
			</tbody>
		</table>
		<a href="/revision" class="float-right">{m.fresh_deft_warbler_edit()}</a>
	</Section>

	<Section title={m.curly_fuzzy_turkey_launch()} href="/thread/overview">
		<table class="w-full">
			<tbody>
				{#each data.posts.items as p, i (i)}
					<tr>
						<td><a href="/thread/{p.id}">{p.title}</a></td>
						<td
							><Time format="relative" date={p.modified} />
							<ParaglideMessage message={m.noble_tidy_boar_lock} inputs={{}}
								>{#snippet content()}<a href="/profile/{p.last_post_by}">{p.last_post_by}</a
									>{/snippet}</ParaglideMessage
							></td
						>
					</tr>
				{/each}
			</tbody>
		</table>
		<a href="/thread/overview" class="float-right">{m.fresh_deft_warbler_edit()}</a>
	</Section>
</div>
