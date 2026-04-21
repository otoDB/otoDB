<script lang="ts">
	import Section from '$lib/Section.svelte';
	import Pager from '$lib/Pager.svelte';
	import { page } from '$app/state';
	import { Platform } from '$lib/schema.js';
	import { enumValues } from '$lib/enums.js';

	let { data } = $props();
</script>

<Section title="Sources">
	<form method="get" class="mb-4 flex flex-wrap items-end gap-3">
		<label class="flex flex-col gap-1">
			<span class="text-sm">Platform</span>
			<select name="platform" class="border" value={data.filters.platform ?? ''}>
				<option value="">All</option>
				{#each enumValues(Platform) as p, i (i)}
					<option value={p}>{p}</option>
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
			Unbound only
		</label>
		<label class="flex items-center gap-1">
			<input
				type="checkbox"
				name="pending"
				value="true"
				checked={data.filters.pending === 'true'}
			/>
			Pending only
		</label>
		<input type="submit" value="Filter" class="border px-3 py-1" />
	</form>

	{#if data.sources?.items?.length}
		<table class="w-full">
			<thead>
				<tr>
					<th>Title</th>
					<th>Platform</th>
					<th>Work</th>
					<th>Added by</th>
					<th>Date</th>
					<th>Status</th>
				</tr>
			</thead>
			<tbody>
				{#each data.sources.items as source (source.id)}
					<tr>
						<td>
							<a href="/source/{source.id}">
								{source.title || source.url}
							</a>
						</td>
						<td>{Platform[source.platform] ?? source.platform}</td>
						<td>
							{#if source.media}
								<a href="/work/{source.media}"
									>{source.media_title || `Work #${source.media}`}</a
								>
							{:else}
								-
							{/if}
						</td>
						<td
							><a href="/profile/{source.added_by.username}"
								>{source.added_by.username}</a
							></td
						>
						<td>{source.published_date ?? '-'}</td>
						<td>
							{#if source.is_pending}
								<span class="text-sky-600">Pending</span>
							{:else}
								Active
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if data.sources.count}
			<Pager
				n_count={data.sources.count}
				page={data.page}
				page_size={data.batchSize}
				base_url={page.url.toString()}
			/>
		{/if}
	{:else}
		<p>No sources found.</p>
	{/if}
</Section>
