<script lang="ts">
	import { ModelNames } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';

	import Section from '$lib/Section.svelte';
	import SongTag from '$lib/SongTag.svelte';
	import { isSOV, isSVO } from '$lib/ui.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTag from '$lib/WorkTag.svelte';

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
		<li>
			<a href="/post/2">{m.noble_fine_iguana_pull()}</a>
		</li>
	</ul>

	<hr class="my-4" />

	<div class="w-full">
		<h2 class="mb-4 text-xl">{m.fuzzy_chunky_niklas_peek()}</h2>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.random as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</div>

	<hr class="my-4" />

	<div class="w-full">
		<h2 class="mb-4 text-xl">{m.big_long_squirrel_kiss()}</h2>
		<div class="grid grid-cols-[repeat(auto-fill,minmax(192px,1fr))] gap-x-4 gap-y-4">
			{#each data.recent as w, i (i)}
				<WorkCard work={w} />
			{/each}
		</div>
	</div>

	<hr class="my-4" />

	<div class="w-full">
		<h2 class="mb-4 text-xl">{m.sea_cute_beaver_file()}</h2>
		<table class="w-full">
			<tbody>
				{#each data.changes as c, i (i)}
					<tr
						><td>{new Date(c.date).toLocaleString()}</td><td
							>{ModelNames[c.model]()}:
							{#if c.model === 'mediawork'}
								<a href="/work/{c.instance.id}">{c.instance.title}</a>
							{:else if c.model === 'mediasong'}
								<a href="/tag/{c.instance.work_tag}">{c.instance.title}</a>
							{:else if c.model === 'tagwork' || c.model === 'wikipage'}
								<WorkTag tag={c.instance} />
							{:else if c.model === 'tagsong'}
								<SongTag tag={c.instance} />
							{/if}
						</td><td>
							{#if isSVO(getLocale())}
								{m.curly_safe_lynx_fond()}
							{/if}
							<a href="/profile/{c.user}">{c.user}</a>
							{#if isSOV(getLocale())}
								{m.curly_safe_lynx_fond()}
							{/if}</td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</div>
</Section>
