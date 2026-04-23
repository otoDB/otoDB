<script lang="ts">
	import { page } from '$app/state';
	import Section from '$lib/Section.svelte';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { enumValues } from '$lib/enums';
	import { userLevelNames } from '$lib/enums/userLevel.js';
	import { Levels, PathsApiProfileSearchGetParametersQueryOrder as OrderEnum } from '$lib/schema';

	let { data } = $props();

	type SortableColumn =
		| 'username'
		| 'works_count'
		| 'revisions_count'
		| 'posts_count'
		| 'comments_count'
		| 'level'
		| 'date_created';

	function sortUrl(col: SortableColumn): string {
		const u = new URL(page.url);
		const desc = `-${col}` as OrderEnum;
		const asc = col as OrderEnum;
		let next: OrderEnum;
		if (data.order === asc) next = desc;
		else if (data.order === desc) next = asc;
		else next = desc;
		u.searchParams.set('order', next);
		u.searchParams.delete('page');
		return u.pathname + u.search;
	}

	function arrow(col: SortableColumn): string {
		if (data.order === col) return '↑';
		if (data.order === `-${col}`) return '↓';
		return '';
	}
</script>

{#snippet sortHeader(col: SortableColumn, label: string)}
	<a href={sortUrl(col)} class="inline-flex items-center justify-end gap-1 whitespace-nowrap">
		<span>{label}</span>
		<span class="inline-block w-3 text-center">{arrow(col)}</span>
	</a>
{/snippet}

<Section title={m.bright_nimble_eagle_glide()}>
	<form target="_self" method="get">
		<table>
			<tbody>
				<tr>
					<td>{m.careful_cozy_elk_dare()}</td>
					<td>
						<input type="text" name="username" value={data.username} />
					</td>
				</tr>
				<tr>
					<td>{m.basic_upper_racoon_type()}</td>
					<td>
						<select name="level" value={data.level ?? ''}>
							<option value="">---</option>
							{#each enumValues(Levels) as lvl, i (i)}
								<option value={lvl}>{userLevelNames[lvl]()}</option>
							{/each}
						</select>
					</td>
				</tr>
			</tbody>
		</table>
		<input type="hidden" name="order" value={data.order} />
		<input type="submit" />
	</form>
	<hr class="my-5" />

	<table class="w-full table-fixed">
		<colgroup>
			<col />
			<col class="w-24" />
			<col class="w-24" />
			<col class="w-24" />
			<col class="w-24" />
			<col class="w-40" />
			<col class="w-32" />
		</colgroup>
		<thead>
			<tr>
				<th class="text-left">
					{@render sortHeader('username', m.careful_cozy_elk_dare())}
				</th>
				<th class="text-right">
					{@render sortHeader('works_count', m.grand_merry_fly_succeed())}
				</th>
				<th class="text-right">
					{@render sortHeader('revisions_count', m.house_patient_cuckoo_trust())}
				</th>
				<th class="text-right">
					{@render sortHeader('posts_count', m.inner_solid_toad_zap())}
				</th>
				<th class="text-right">
					{@render sortHeader('comments_count', m.same_broad_haddock_pinch())}
				</th>
				<th class="text-right">
					{@render sortHeader('level', m.basic_upper_racoon_type())}
				</th>
				<th class="text-right">
					{@render sortHeader('date_created', m.stale_early_squirrel_prosper())}
				</th>
			</tr>
		</thead>
		<tbody>
			{#each data.results?.items ?? [] as user, i (i)}
				<tr>
					<td class="truncate text-left">
						<a href="/profile/{user.username}">{user.username}</a>
					</td>
					<td class="text-right">{user.works_count}</td>
					<td class="text-right">{user.revisions_count}</td>
					<td class="text-right">{user.posts_count}</td>
					<td class="text-right">{user.comments_count}</td>
					<td class="text-right">{userLevelNames[user.level]()}</td>
					<td class="text-right">
						{user.date_created ? new Date(user.date_created).toLocaleDateString() : ''}
					</td>
				</tr>
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
