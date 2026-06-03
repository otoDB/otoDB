<script lang="ts">
	import { page } from '$app/state';
	import Pager from '$lib/Pager.svelte';
	import Section from '$lib/Section.svelte';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import { m } from '$lib/paraglide/messages';
	import { WikiKind } from '$lib/schema';

	let { data } = $props();

	function hrefFor(row: (typeof data.results.items)[number]): string {
		if (row.kind === WikiKind.tag) return `/tag/${row.key}`;
		if (row.kind === WikiKind.work) return `/work/${row.key}`;
		return `/wiki/${row.key}`;
	}

	function langDisplay(id: number): string {
		const key = resolveLanguageKeyById(id);
		return key ? languages[key].name : '—';
	}
</script>

<Section title={m.curly_zesty_pelican_aim()}>
	<form method="get" class="mb-4 flex flex-wrap items-end gap-1">
		<label class="flex flex-col text-sm">
			<input type="text" name="q" value={data.q} placeholder="{m.mean_top_antelope_love()}..." />
		</label>
		<input type="submit" />
	</form>

	{#if data.results.items.length === 0}
		<p>{m.tame_dirty_goldfish_flow()}</p>
	{:else}
		<table class="w-full">
			<thead>
				<tr>
					<th>{m.large_factual_octopus_exhale()}</th>
					<th>{m.hour_loud_squirrel_ascend()}</th>
					<th>{m.lower_full_opossum_bless()}</th>
				</tr>
			</thead>
			<tbody>
				{#each data.results.items as row, i (i)}
					<tr>
						<td><a href={hrefFor(row)}>{row.title}</a></td>
						<td>{row.langs.map(langDisplay).join(', ')}</td>
						<td>
							{#if row.last_edited_at}
								{new Date(row.last_edited_at).toLocaleDateString()}
							{:else}
								—
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if data.results.count}
			<Pager
				n_count={data.results.count}
				page={data.page}
				page_size={data.batch_size}
				base_url={page.url.toString()}
			/>
		{/if}
	{/if}
</Section>
