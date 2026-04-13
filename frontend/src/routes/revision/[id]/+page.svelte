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
	import {
		getLanguageId,
		isSOV,
		isSVO,
		languages,
		resolveLanguageKeyById
	} from '$lib/enums/Languages';
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

	type D = () => string;
	const V_to_D =
		(r: (b: number) => string, fs: Record<string, { nameFn: D }>) =>
		(v: number): D =>
			fs[r(v)].nameFn;
	const SV_to_D =
		(r: (b: number) => string, fs: Record<string, { name: string }>) =>
		(v: number): D =>
		() =>
			fs[r(v)].name;
	const SR_to_D =
		<T extends number>(r: Record<T, string>) =>
		(v: number): D =>
		() =>
			r[v as T];
	const A_to_D = (r: D[]) => (v: number) => r[v];
	const SA_to_D =
		(r: string[]) =>
		(v: number): D =>
		() =>
			r[v];
	const expand_bit_field =
		(r: (b: number) => string, fs: Record<string, { nameFn: D }>) =>
		(v: number): D =>
		() =>
			[...v.toString(2)]
				.reduce(
					(a, e, i, aa) =>
						e === '1' ? [...a, V_to_D(r, fs)(Math.pow(2, aa.length - 1 - i))()] : a,
					[] as string[]
				)
				.join(', ') || 'N/A';

	const Languages = SV_to_D(resolveLanguageKeyById, languages);

	const ValueDisplayMap: Record<string, Record<string, (v: number) => D>> = {
		mediawork: {
			rating: A_to_D(Rating)
		},
		tagwork: {
			category: A_to_D(WorkTagCategory),
			media_type: expand_bit_field(resolveMediaTypeKeyById, mediaTypes)
		},
		tagsong: {
			category: A_to_D(SongTagCategory)
		},
		tagworkconnection: {
			site: SV_to_D(resolveTagWorkConnectionNameById, TagWorkConnection)
		},
		mediasongconnection: {
			site: SV_to_D(resolveSongConnectionNameById, SongConnection)
		},
		tagworkmediaconnection: {
			site: SV_to_D(resolveMediaConnectionNameById, MediaConnection)
		},
		tagworkcreatorconnection: {
			site: SV_to_D(resolveProfileConnectionNameById, ProfileConnection)
		},
		tagworklangpreference: {
			lang: Languages
		},
		tagsonglangpreference: {
			lang: Languages
		},
		workrelation: {
			relation: A_to_D(WorkRelationTypes)
		},
		songrelation: {
			relation: A_to_D(SongRelationTypes)
		},
		tagworkinstance: {
			creator_roles: expand_bit_field(resolveCreatorRoleKeyById, creatorRole)
		},
		wikipage: {
			lang: Languages
		},
		worksource: {
			platform: SA_to_D(Platform),
			thumbnail_mime: SR_to_D(MimeType),
			work_origin: A_to_D(WorkOrigin),
			work_status: A_to_D(WorkStatus)
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
		{#each data.routes as [r, ecs], i (i)}
			<li>{Route[resolveRouteKeyById(r)].title}</li>
			<li class="ml-2 list-none">
				<ul>
					{#each ecs as [[ent_type, ent_id], ec], j (j)}
						<li>
							<a href={buildEntityRoutes(ent_type, ent_id)}>
								{buildEntityRoutes(ent_type, ent_id)}
							</a>
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
	<Pager n_count={data.changes.count} page={data.page} page_size={data.batch_size} />
</Section>
