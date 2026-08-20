<script lang="ts">
	import Section from '$lib/Section.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { Platform } from '$lib/schema.js';
	import { enumValues, PlatformNames } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<Section title={data.head.title}>
	<form method="get" class="mb-4 flex flex-wrap items-end gap-3">
		<label class="flex flex-col gap-1">
			<span class="text-sm">Platform</span>
			<select name="platform" class="border" value={data.filters.platform ?? ''}>
				<option value="">All</option>
				{#each enumValues(Platform) as p, i (i)}
					<option value={p}>{PlatformNames[p]}</option>
				{/each}
			</select>
		</label>
		<label class="flex items-center gap-1">
			<input
				type="checkbox"
				name="unbound"
				value="true"
				checked={data.filters.unbound === 'true'}
			/>
			{m.top_bald_piranha_clap()}
		</label>
		<label class="flex items-center gap-1">
			<input
				type="checkbox"
				name="pending"
				value="true"
				checked={data.filters.pending === 'true'}
			/>
			{m.mean_simple_flea_aid()}
		</label>
		<input type="submit" value="Filter" class="border px-3 py-1" />
	</form>

	{#if data.sources?.items?.length}
		<div class="overflow-x-auto">
			<table class="w-full min-w-4xl table-fixed wrap-anywhere">
				<colgroup>
					<col />
					<col class="w-40" />
					<col class="w-2/12" />
					<col class="w-2/12" />
					<col class="w-28" />
					<col class="w-24" />
				</colgroup>
				<thead>
					<tr>
						<th>{m.large_factual_octopus_exhale()}</th>
						<th class="text-center whitespace-nowrap">{m.sour_swift_sparrow_spin()}</th>
						<th>{m.grand_merry_fly_succeed()}</th>
						<th>{m.each_born_quail_gleam()}</th>
						<th class="text-center whitespace-nowrap">{m.super_agent_pigeon_aim()}</th>
						<th class="text-center whitespace-nowrap">{m.just_noisy_moth_beam()}</th>
					</tr>
				</thead>
				<tbody>
					{#each data.sources.items as source (source.id)}
						<tr>
							<td>
								<a href="/upload/{source.id}">
									{source.title || source.url}
								</a>
							</td>
							<td class="text-center whitespace-nowrap">{PlatformNames[source.platform]}</td>
							<td>
								{#if source.media}
									<a href="/work/{source.media}">{source.media_title || `Work #${source.media}`}</a>
								{:else}
									-
								{/if}
							</td>
							<td>
								<a href="/profile/{source.added_by.username}">{source.added_by.username}</a>
							</td>
							<td class="text-center whitespace-nowrap">{source.published_date ?? '-'}</td>
							<td class="text-center whitespace-nowrap">
								{#if source.is_pending}
									<span class="text-sky-600">{m.such_actual_okapi_dare()}</span>
								{:else}
									Active
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		{#if data.sources.count}
			<Pager
				n_count={data.sources.count}
				page_size={data.batchSize}
				base_url={page.url.toString()}
			/>
		{/if}
	{:else}
		<p>{m.dull_every_wasp_win()}</p>
	{/if}
</Section>
