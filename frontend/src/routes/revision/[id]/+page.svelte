<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import {
		buildEntityRoutes,
		MimeType,
		Platform,
		Rating,
		SongRelationTypes,
		SongTagCategory,
		WorkOrigin,
		WorkRelationTypes,
		WorkStatus,
		WorkTagCategory
	} from '$lib/enums.js';
	import { creatorRole, resolveCreatorRoleKeyById } from '$lib/enums/CreatorRole';
	import { isSOV, isSVO, languages, resolveLanguageKeyById } from '$lib/enums/Languages';
	import { MediaConnection, resolveMediaConnectionNameById } from '$lib/enums/MediaConnection';
	import { mediaTypes, resolveMediaTypeKeyById } from '$lib/enums/MediaType.js';
	import {
		ProfileConnection,
		resolveProfileConnectionNameById
	} from '$lib/enums/ProfileConnection';
	import { resolveRouteKeyById, Route } from '$lib/enums/Route.js';
	import { resolveSongConnectionNameById, SongConnection } from '$lib/enums/SongConnection';
	import {
		resolveTagWorkConnectionNameById,
		TagWorkConnection
	} from '$lib/enums/TagWorkConnection';
	import { hasUserLevelOld } from '$lib/enums/UserLevel.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	type DisplayFunction = () => string;
	const Values_to_DisplayFunction =
		(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
		(v: number): DisplayFunction =>
			fs[r(v)].nameFn;
	const StraightValues_to_DisplayFunction =
		(r: (b: number) => string, fs: Record<string, { name: string }>) =>
		(v: number): DisplayFunction =>
		() =>
			fs[r(v)].name;
	const StraightRecord_to_DisplayFunction =
		<T extends number>(r: Record<T, string>) =>
		(v: number): DisplayFunction =>
		() =>
			r[v as T];
	const Array_to_DisplayFunction = (r: DisplayFunction[]) => (v: number) => r[v];
	const StraightArray_to_DisplayFunction =
		(r: string[]) =>
		(v: number): DisplayFunction =>
		() =>
			r[v];
	const expand_bit_field =
		(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
		(v: number): DisplayFunction =>
		() =>
			[...v.toString(2)]
				.reduce(
					(a, e, i, aa) =>
						e === '1'
							? [
									...a,
									Values_to_DisplayFunction(
										r,
										fs
									)(Math.pow(2, aa.length - 1 - i))()
								]
							: a,
					[] as string[]
				)
				.join(', ') || 'N/A';

	const Languages = StraightValues_to_DisplayFunction(resolveLanguageKeyById, languages);

	const ValueDisplayMap: Record<string, Record<string, (v: number) => DisplayFunction>> = {
		mediawork: {
			rating: Array_to_DisplayFunction(Rating)
		},
		tagwork: {
			category: Array_to_DisplayFunction(WorkTagCategory),
			media_type: expand_bit_field(resolveMediaTypeKeyById, mediaTypes)
		},
		tagsong: {
			category: Array_to_DisplayFunction(SongTagCategory)
		},
		tagworkconnection: {
			site: StraightValues_to_DisplayFunction(
				resolveTagWorkConnectionNameById,
				TagWorkConnection
			)
		},
		mediasongconnection: {
			site: StraightValues_to_DisplayFunction(resolveSongConnectionNameById, SongConnection)
		},
		tagworkmediaconnection: {
			site: StraightValues_to_DisplayFunction(resolveMediaConnectionNameById, MediaConnection)
		},
		tagworkcreatorconnection: {
			site: StraightValues_to_DisplayFunction(
				resolveProfileConnectionNameById,
				ProfileConnection
			)
		},
		tagworklangpreference: {
			lang: Languages
		},
		tagsonglangpreference: {
			lang: Languages
		},
		workrelation: {
			relation: Array_to_DisplayFunction(WorkRelationTypes)
		},
		songrelation: {
			relation: Array_to_DisplayFunction(SongRelationTypes)
		},
		tagworkinstance: {
			creator_roles: expand_bit_field(resolveCreatorRoleKeyById, creatorRole)
		},
		wikipage: {
			lang: Languages
		},
		worksource: {
			platform: StraightArray_to_DisplayFunction(Platform),
			thumbnail_mime: StraightRecord_to_DisplayFunction(MimeType),
			work_origin: Array_to_DisplayFunction(WorkOrigin),
			work_status: Array_to_DisplayFunction(WorkStatus)
		}
	};

	const displayValue = (
		type: keyof typeof ValueDisplayMap,
		col: string,
		val: string | null | undefined
	) => {
		const handler = ValueDisplayMap[type]?.[col];
		return decodeURIComponent((val ? (handler ? handler(+val)() : val) : null) ?? 'None');
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
	{#if hasUserLevelOld(data.user?.level, 'ADMIN') && data.revision.id > 1}<button
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
		{#each data.routes as { route, entities }, i (i)}
			<li>{Route[resolveRouteKeyById(route)].title()}</li>
			<li class="ml-2 list-none">
				<ul>
					{#each entities as { ent_type, ent_id, rcs }, j (j)}
						<li>
							<a href={buildEntityRoutes(ent_type, ent_id)}>
								{buildEntityRoutes(ent_type, ent_id)}
							</a>
						</li>
						<li class="list-none">
							<table class="inline-block">
								<tbody>
									{#each rcs as c, k (k)}
										{#if c.target_column}
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
										{/if}
									{/each}
								</tbody>
							</table>
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ul>
	<Pager n_count={data.changes.count} page={data.page} page_size={data.batch_size} />
</Section>
