<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import {
		EntityModelRoutes,
		MediaType,
		MimeType,
		Platform,
		Rating,
		Role,
		SongRelationTypes,
		SongTagCategory,
		UserLevel,
		WorkOrigin,
		WorkRelationTypes,
		WorkStatus,
		WorkTagCategory
	} from '$lib/enums.js';
	import { languages, resolveLanguageKeyById } from '$lib/Languages.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/Languages.js';
	import { resolveTagWorkConnectionNameById, TagWorkConnection } from '$lib/TagWorkConnection.js';
	import { resolveSongConnectionNameById, SongConnection } from '$lib/SongConnection.js';
	import { MediaConnection, resolveMediaConnectionNameById } from '$lib/MediaConnection.js';
	import { ProfileConnection, resolveProfileConnectionNameById } from '$lib/ProfileConnection.js';

	let { data } = $props();
	let routes = $derived(
		Object.values(Object.groupBy(data.changes.items, (c) => c.route))
			.map((rent) => [
				rent[0].route,
				Object.values(Object.groupBy(rent, (c) => c.ent_type + c.ent_id))
					// .map((cs) => cs.filter((c) => c.target_value !== null))
					// Setting to null may be significant change
					.map((cs) => cs.filter((c) => Object.hasOwn(EntityModelRoutes, c.ent_type)))
					.filter((ec) => ec.length)
					.map((tg) => [[tg[0].ent_type, tg[0].ent_id], tg])
			])
			.filter((rc) => rc[1].length)
	);

	const expand_bit_field = (names) => (v) =>
		[...parseInt(v, 10).toString(2)]
			.reduce(
				(a, e, i, aa) => (e === '1' ? [...a, names[Math.pow(2, aa.length - 1 - i)]()] : a),
				[]
			)
			.join(', ') || 'N/A';

	// TODO: need more refactor
	// TODO: `decodeURIComponent`を入れる必要があったが返ってくる値にそれをしないとならないものがあるとは思えないので削除．
	const displayValue = (type: string, col: string, val: unknown): string => {
		switch (type) {
			case 'mediawork':
				switch (col) {
					case 'rating':
						return Rating[val as number]();
				}
				break;
			case 'tagwork':
				switch (col) {
					case 'category':
						return WorkTagCategory[val as number]();
					case 'media_type':
						return expand_bit_field(MediaType)(val);
				}
				break;
			case 'tagsong':
				switch (col) {
					case 'category':
						return SongTagCategory[val as number]();
				}
				break;
			case 'tagworkconnection':
				switch (col) {
					case 'site':
						return TagWorkConnection[resolveTagWorkConnectionNameById(val as number)]
							.name;
				}
				break;
			case 'mediasongconnection':
				switch (col) {
					case 'site':
						return SongConnection[resolveSongConnectionNameById(val as number)].name;
				}
				break;
			case 'tagworkmediaconnection':
				switch (col) {
					case 'site':
						return MediaConnection[resolveMediaConnectionNameById(val as number)].name;
				}
				break;
			case 'tagworkcreatorconnection':
				switch (col) {
					case 'site':
						return ProfileConnection[resolveProfileConnectionNameById(val as number)]
							.name;
				}
				break;
			case 'tagworklangpreference':
				switch (col) {
					case 'lang':
						return languages[resolveLanguageKeyById(val as number)].name;
				}
				break;
			case 'tagsonglangpreference':
				switch (col) {
					case 'lang':
						return languages[resolveLanguageKeyById(val as number)].name;
				}
				break;
			case 'workrelation':
				switch (col) {
					case 'relation':
						return WorkRelationTypes[val as number]();
				}
				break;
			case 'songrelation':
				switch (col) {
					case 'relation':
						return SongRelationTypes[val as number]();
				}
				break;
			case 'tagworkinstance':
				switch (col) {
					case 'creator_roles':
						return expand_bit_field(Role)(val);
				}
				break;
			case 'wikipage':
				switch (col) {
					case 'lang':
						return languages[resolveLanguageKeyById(val as number)].name;
				}
				break;
			case 'worksource':
				switch (col) {
					case 'platform':
						return Platform[val as number];
					case 'thumbnail_mime':
						return MimeType[val as keyof typeof MimeType];
					case 'work_origin':
						return WorkOrigin[val as number]();
					case 'work_status':
						return WorkStatus[val as number]();
				}
				break;
		}
		return 'None';
	};
</script>

<Section title="{m.arable_direct_swan_glow()} #{data.revision.id}">
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.revision.user}">{data.revision.user}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	{#if data.revision.message}<h4 class="my-5">{data.revision.message}</h4>{/if}
	{#if data.user?.level >= UserLevel.ADMIN && data.revision.id > 1}<button
			class="my-5"
			onclick={async () => {
				if (!confirm('Are you sure?')) return;
				await client.POST('/api/history/rollback', {
					fetch,
					params: { query: { revision_id: data.revision.id } }
				});
				invalidateAll();
			}}>Revert changes made in this revision</button
		>{/if}
	<ul class="my-5">
		{#each routes as [r, ecs], i (i)}
			<li>{Route[r]}</li>
			<li class="ml-2 list-none">
				<ul>
					{#each ecs as [[ent_type, ent_id], ec], j (j)}
						<li>
							<a href="/{EntityModelRoutes[ent_type]}/{ent_id}"
								>/{EntityModelRoutes[ent_type]}/{ent_id}</a
							>
						</li>
						<li class="list-none">
							<table class="inline-block">
								<tbody>
									{#each ec as c, k (k)}
										<tr
											><td
												>{#if !(c.target_type === ent_type && c.tg_id === ent_id)}{c.target_type}
													#{c.tg_id}{/if}
												{c.target_column}</td
											>
											<td
												>{#if c.deleted}Deleted{:else}<pre>{displayValue(
															c.target_type,
															c.target_column,
															c.target_value
														)}</pre>{/if}</td
											></tr
										>
									{/each}
								</tbody>
							</table>
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ul>
	<Pager n_count={data.changes?.count} page={data.page} page_size={data.batch_size} />
</Section>
