<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import {
		buildEntityRoutes,
		MimeType,
		PlatformNames,
		RatingNames,
		SongRelationNames,
		SongTagCategoryNames,
		WorkOriginNames,
		WorkRelationNames,
		WorkStatusNames,
		type Enum
	} from '$lib/enums.js';
	import { creatorRole, resolveCreatorRoleKeyById } from '$lib/enums/creatorRole.js';
	import { isSOV, isSVO, languages, resolveLanguageKeyById } from '$lib/enums/language.js';
	import { mediaConnectionMap } from '$lib/enums/mediaConnection.js';
	import { mediaTypes, resolveMediaTypeKeyById } from '$lib/enums/mediaType.js';
	import { profileConnectionMap } from '$lib/enums/profileConnection.js';
	import { routeNames } from '$lib/enums/route.js';
	import { songConnectionMap } from '$lib/enums/songConnection.js';
	import { TagWorkConnectionMap } from '$lib/enums/tagWorkConnection.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import { WorkTagCategoryMap } from '$lib/enums/workTagCategory.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import { Levels, PostCategory } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	type DisplayFunction = () => string;
	const EnumMap_to_DisplayFunction =
		<E extends Enum<E>>(fs: Record<E[keyof E], { name: string }>) =>
		(v: number): DisplayFunction =>
		() =>
			fs[v as E[keyof E]].name;
	const EnumValues_to_DisplayFunction =
		<E extends Enum<E>>(fs: Record<E[keyof E], { nameFn: DisplayFunction }>) =>
		(v: number): DisplayFunction =>
			fs[v as E[keyof E]].nameFn;
	const Values_to_DisplayFunction =
		(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
		(v: number): DisplayFunction =>
			fs[r(v)].nameFn;
	const StraightValues_to_DisplayFunction =
		(r: (b: number) => string, fs: Record<string, { name: string }>) =>
		(v: number): DisplayFunction =>
		() =>
			fs[r(v)].name;
	const EnumStraightRecord_to_DisplayFunction =
		<E extends Enum<E>>(fs: Record<E[keyof E], string>) =>
		(v: number): DisplayFunction =>
		() =>
			fs[v as E[keyof E]];
	const StraightRecord_to_DisplayFunction =
		<T extends number>(r: Record<T, string>) =>
		(v: number): DisplayFunction =>
		() =>
			r[v as T];
	const EnumRecord_to_DisplayFunction =
		<E extends Enum<E>>(fs: Record<E[keyof E], DisplayFunction>) =>
		(v: number): DisplayFunction =>
			fs[v as E[keyof E]];
	const expand_bit_field =
		(r: (b: number) => string, fs: Record<string, { nameFn: DisplayFunction }>) =>
		(v: number): DisplayFunction =>
		() =>
			[...v.toString(2)]
				.reduce(
					(a, e, i, aa) =>
						e === '1'
							? [...a, Values_to_DisplayFunction(r, fs)(1 << (aa.length - 1 - i))()]
							: a,
					[] as string[]
				)
				.join(', ') || 'N/A';

	const Languages = StraightValues_to_DisplayFunction(resolveLanguageKeyById, languages);

	const ValueDisplayMap: Record<string, Record<string, (v: number) => DisplayFunction>> = {
		mediawork: {
			rating: EnumRecord_to_DisplayFunction(RatingNames)
		},
		tagwork: {
			category: EnumValues_to_DisplayFunction(WorkTagCategoryMap),
			media_type: expand_bit_field(resolveMediaTypeKeyById, mediaTypes)
		},
		tagsong: {
			category: EnumMap_to_DisplayFunction(SongTagCategoryNames)
		},
		tagworkconnection: {
			site: EnumMap_to_DisplayFunction(TagWorkConnectionMap)
		},
		mediasongconnection: {
			site: EnumMap_to_DisplayFunction(songConnectionMap)
		},
		tagworkmediaconnection: {
			site: EnumMap_to_DisplayFunction(mediaConnectionMap)
		},
		tagworkcreatorconnection: {
			site: EnumMap_to_DisplayFunction(profileConnectionMap)
		},
		tagworklangpreference: {
			lang: Languages
		},
		tagsonglangpreference: {
			lang: Languages
		},
		workrelation: {
			relation: EnumRecord_to_DisplayFunction(WorkRelationNames)
		},
		songrelation: {
			relation: EnumRecord_to_DisplayFunction(SongRelationNames)
		},
		tagworkinstance: {
			creator_roles: expand_bit_field(resolveCreatorRoleKeyById, creatorRole)
		},
		wikipage: {
			lang: Languages
		},
		worksource: {
			platform: EnumStraightRecord_to_DisplayFunction(PlatformNames),
			thumbnail_mime: StraightRecord_to_DisplayFunction(MimeType),
			work_origin: EnumRecord_to_DisplayFunction(WorkOriginNames),
			work_status: EnumRecord_to_DisplayFunction(WorkStatusNames)
		}
	};

	const displayValue = (
		type: keyof typeof ValueDisplayMap,
		col: string,
		val: string | null | undefined
	) => {
		if (val === null || val === undefined) return 'None';
		const handler = ValueDisplayMap[type]?.[col];
		return handler ? handler(+val)() : val;
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
	{#if hasUserLevel(data.user?.level, Levels.Admin) && data.revision.id !== '1'}<button
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
	{#if data.user && data.user.username !== data.revision.user}
		<button
			onclick={() =>
				goto(
					`/post/new?category=${PostCategory.Gardening}&entity=@${data.revision.user}&title=${m.silly_quiet_fireant_quell({ id: data.revision.id })}`
				)}>{m.frail_loose_gecko_play({ user: data.revision.user })}</button
		>
	{/if}

	<ul class="my-5">
		{#each data.routes as { route, entities }, i (i)}
			<li>{routeNames[route]()}</li>
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
