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
	import { creatorRole } from '$lib/enums/CreatorRole';
	import { isSOV, isSVO, languages, resolveLanguageKeyById } from '$lib/enums/Languages';
	import { MediaConnection, resolveMediaConnectionNameById } from '$lib/enums/MediaConnection';
	import { mediaTypes } from '$lib/enums/MediaType.js';
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
	import { hasUserLevel, resolveUserLevelById } from '$lib/enums/UserLevel.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	// TODO: need more refactor
	// TODO: `decodeURIComponent`を入れる必要があったが返ってくる値にそれをしないとならないものがあるとは思えないので削除．
	// TODO: `tagwork.media_type` および `tagworkinstance.creator_roles` がad-hocすぎる
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
					case 'media_type': {
						const [isGame, isFilm, isShow, isAnime] = parseInt(val as string, 10)
							.toString(2)
							.padStart(4, '0')
							.split('')
							.map((b) => b === '1');

						if (!isGame && !isFilm && !isShow && !isAnime) return 'N/A';

						return [
							isAnime ? mediaTypes['ANIME'].nameFn() : '',
							isShow ? mediaTypes['SHOW'].nameFn() : '',
							isFilm ? mediaTypes['FILM'].nameFn() : '',
							isGame ? mediaTypes['GAME'].nameFn() : ''
						].join(', ');
					}
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
					case 'creator_roles': {
						const [isThanks, isArtwork, isMusic, isDirector, isVisuals, isAudio] =
							parseInt(val as string, 10)
								.toString(2)
								.padStart(6, '0')
								.split('')
								.map((b) => b === '1');
						if (
							!isThanks &&
							!isArtwork &&
							!isMusic &&
							!isDirector &&
							!isVisuals &&
							!isAudio
						)
							return 'N/A';
						return [
							isAudio ? creatorRole['AUDIO'].nameFn() : '',
							isVisuals ? creatorRole['VISUALS'].nameFn() : '',
							isDirector ? creatorRole['DIRECTOR'].nameFn() : '',
							isMusic ? creatorRole['MUSIC'].nameFn() : '',
							isArtwork ? creatorRole['ARTWORK'].nameFn() : '',
							isThanks ? creatorRole['THANKS'].nameFn() : ''
						].join(', ');
					}
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
	{#if data.user && hasUserLevel(resolveUserLevelById(data.user.level), 'ADMIN') && data.revision.id > 1}<button
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
												>{#if c.deleted}Deleted{:else}<pre>{decodeURIComponent(
															displayValue(
																c.target_type,
																c.target_column,
																c.target_value
															)
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
