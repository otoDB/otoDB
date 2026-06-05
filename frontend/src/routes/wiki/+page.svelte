<script lang="ts">
	import { page } from '$app/state';
	import Pager from '$lib/Pager.svelte';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import { m } from '$lib/paraglide/messages';
	import { WikiKind } from '$lib/schema';
	import { getTagDisplayName } from '$lib/ui';

	let { data } = $props();

	type Row = (typeof data.results.items)[number];

	function hrefFor(row: Row): string {
		if (row.tag) return `/tag/${row.tag.slug}`;
		if (row.work) return `/work/${row.work.id}`;
		if (row.docs) return `/wiki/${row.docs.slug}`;
		return '#';
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
		<select name="kind">
			<option value="">{m.keen_soft_crow_relish()}</option>
			<option value={WikiKind.tag} selected={data.kind === WikiKind.tag}>
				{m.empty_legal_chicken_taste()}
			</option>
			<option value={WikiKind.work} selected={data.kind === WikiKind.work}>
				{m.grand_merry_fly_succeed()}
			</option>
			<option value={WikiKind.docs} selected={data.kind === WikiKind.docs}>
				{m.nice_close_goldfish_taste()}
			</option>
		</select>
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
						<td>
							<a href={hrefFor(row)}>
								{#if row.tag}
									{getTagDisplayName(row.tag)}
								{:else if row.work}
									{row.work.title ?? `#${row.work.id}`}
								{:else if row.docs}
									{row.docs.title ?? row.docs.slug}
								{/if}
							</a>
						</td>
						<td>{row.langs.map(langDisplay).join(', ')}</td>
						<td>
							{#if row.last_edited_at}
								<Time date={row.last_edited_at} format="relative" />
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
