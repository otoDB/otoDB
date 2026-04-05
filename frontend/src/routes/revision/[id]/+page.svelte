<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import {
		EntityModelRoutes,
		Languages,
		MediaConnectionTypes,
		MediaType,
		MimeType,
		Platform,
		ProfileConnectionTypes,
		Rating,
		Role,
		Route,
		SongConnectionTypes,
		SongRelationTypes,
		SongTagCategory,
		TagWorkConnectionTypes,
		UserLevel,
		WorkOrigin,
		WorkRelationTypes,
		WorkStatus,
		WorkTagCategory
	} from '$lib/enums.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/enums';

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

	const ValueDisplayMap = {
		mediawork: {
			rating: Rating
		},
		tagwork: {
			category: WorkTagCategory,
			media_type: expand_bit_field(MediaType)
		},
		tagsong: {
			category: SongTagCategory
		},
		tagworkconnection: {
			site: TagWorkConnectionTypes
		},
		mediasongconnection: {
			site: SongConnectionTypes
		},
		tagworkmediaconnection: {
			site: MediaConnectionTypes
		},
		tagworkcreatorconnection: {
			site: ProfileConnectionTypes
		},
		tagworklangpreference: {
			lang: Languages
		},
		tagsonglangpreference: {
			lang: Languages
		},
		workrelation: {
			relation: WorkRelationTypes
		},
		songrelation: {
			relation: SongRelationTypes
		},
		tagworkinstance: {
			creator_roles: expand_bit_field(Role)
		},
		wikipage: {
			lang: Languages
		},
		worksource: {
			platform: Platform,
			thumbnail_mime: MimeType,
			work_origin: WorkOrigin,
			work_status: WorkStatus
		}
	};

	const displayValue = (type: string, col: string, val: string | null) => {
		const handler = ValueDisplayMap[type]?.[col];
		const raw = handler
			? typeof handler === 'function'
				? handler(val)
				: typeof handler[val] === 'function'
					? handler[val]()
					: handler[val]
			: (val ?? 'None');
		const result = typeof raw === 'string' ? decodeURIComponent(raw) : raw;
		return result;
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
