<script lang="ts">
	import { page } from '$app/state';
	import { buildEntityRoutes, fieldEnumOptions } from '$lib/enums.js';
	import { routeNames } from '$lib/enums/route.js';
	import Pager from '$lib/Pager.svelte';
	import { m } from '$lib/paraglide/messages';
	import { HistoricalEntities, type Route } from '$lib/schema';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	let { data } = $props();

	// When typed field maps to an enum, the value filters become dropdowns
	let changedField = $state(data.filters.changed_field ?? '');
	const valueOptions = $derived(fieldEnumOptions[changedField.trim()] ?? []);

	const entityOptions = {
		[HistoricalEntities.mediawork]: m.grand_merry_fly_succeed,
		[HistoricalEntities.tagwork]: m.empty_legal_chicken_taste,
		[HistoricalEntities.tagsong]: m.dull_plain_angelfish_cuddle,
		[HistoricalEntities.mediasong]: m.grand_nice_pony_belong,
		[HistoricalEntities.worksource]: m.extra_brave_tapir_skip,
		[HistoricalEntities.wikipage]: m.curly_zesty_pelican_aim
	} as Record<HistoricalEntities, () => string>;

	let filtersOpen = $state(Object.values(data.filters).some((v) => v !== undefined));
</script>

<Section title={m.giant_away_scallop_hike()}>
	<form target="_self" method="get">
		<details bind:open={filtersOpen}>
			<summary>{m.mean_top_antelope_love()}</summary>
			<div
				class="grid grid-cols-[max-content_minmax(0,1fr)] items-center gap-x-3 gap-y-2 md:grid-cols-[max-content_minmax(0,1fr)_max-content_minmax(0,1fr)_max-content_minmax(0,1fr)]"
			>
				<label for="filter-username" class="self-start">{m.fuzzy_crazy_cobra_lead()}</label>
				<input
					id="filter-username"
					class="self-start"
					type="text"
					name="username"
					value={data.filters.username ?? ''}
				/>

				<label for="filter-entity" class="self-start">{m.early_loved_panda_link()}</label>
				<select id="filter-entity" class="self-start" name="entity">
					<option value="" selected={data.filters.entity == null}>
						{m.keen_soft_crow_relish()}
					</option>
					{#each Object.entries(entityOptions) as [value, name] (value)}
						<option {value} selected={data.filters.entity === value}>{name()}</option>
					{/each}
				</select>

				<label for="filter-routes" class="self-start">{m.arable_direct_swan_glow()}</label>
				<select id="filter-routes" name="routes" multiple size="6">
					{#each Object.entries(routeNames) as [key, name] (key)}
						<option value={key} selected={data.filters.routes?.includes(Number(key) as Route)}>
							{name()}
						</option>
					{/each}
				</select>

				<label for="filter-reason">{m.weary_spicy_fly_attend()}</label>
				<input
					id="filter-reason"
					class="md:col-span-5"
					type="text"
					name="reason"
					value={data.filters.reason ?? ''}
				/>

				<label for="filter-since">{m.fancy_round_quail_begin()}</label>
				<input id="filter-since" type="date" name="since" value={data.filters.since ?? ''} />
				<label for="filter-until">{m.moving_least_swift_stop()}</label>
				<input id="filter-until" type="date" name="until" value={data.filters.until ?? ''} />

				<label for="filter-is-new" class="md:col-start-1">{m.young_fresh_filly_appear()}</label>
				<select id="filter-is-new" name="is_new">
					<option value="" selected={data.filters.is_new == null}>---</option>
					<option value="true" selected={data.filters.is_new === true}>
						{m.young_fresh_filly_appear()}
					</option>
					<option value="false" selected={data.filters.is_new === false}>
						{m.old_keen_bison_revise()}
					</option>
				</select>
				<label for="filter-is-deleted">{m.stark_grim_raven_erase()}</label>
				<input
					id="filter-is-deleted"
					class="justify-self-start md:col-span-3"
					type="checkbox"
					name="is_deleted"
					value="true"
					checked={data.filters.is_deleted ?? false}
				/>

				<label for="filter-changed-field">{m.flat_neat_swan_mark()}</label>
				<input
					id="filter-changed-field"
					type="text"
					name="changed_field"
					list="changed-field-options"
					bind:value={changedField}
				/>
				<datalist id="changed-field-options">
					{#each Object.keys(fieldEnumOptions) as field (field)}
						<option value={field}></option>
					{/each}
				</datalist>
				<label for="filter-changed-from">{m.warm_plain_lion_revert()}</label>
				{#if valueOptions.length}
					<select id="filter-changed-from" name="changed_from">
						<option value="" selected={!data.filters.changed_from}>---</option>
						{#each valueOptions as o (o.value + o.label())}
							<option value={o.value} selected={data.filters.changed_from === o.value}>
								{o.label()}
							</option>
						{/each}
					</select>
				{:else}
					<input
						id="filter-changed-from"
						type="text"
						name="changed_from"
						value={data.filters.changed_from ?? ''}
					/>
				{/if}
				<label for="filter-changed-value">{m.ripe_bold_lion_rate()}</label>
				{#if valueOptions.length}
					<select id="filter-changed-value" name="changed_value">
						<option value="" selected={!data.filters.changed_value}>---</option>
						{#each valueOptions as o (o.value + o.label())}
							<option value={o.value} selected={data.filters.changed_value === o.value}>
								{o.label()}
							</option>
						{/each}
					</select>
				{:else}
					<input
						id="filter-changed-value"
						type="text"
						name="changed_value"
						value={data.filters.changed_value ?? ''}
					/>
				{/if}

				<label for="filter-added-tags">{m.lush_green_frog_attach()}</label>
				<input
					id="filter-added-tags"
					type="text"
					name="added_tags"
					placeholder={m.petty_fuzzy_fox_ask()}
					value={data.filters.added_tags?.join(' ') ?? ''}
				/>
				<label for="filter-removed-tags">{m.dry_red_wasp_detach()}</label>
				<input
					id="filter-removed-tags"
					type="text"
					name="removed_tags"
					placeholder={m.petty_fuzzy_fox_ask()}
					value={data.filters.removed_tags?.join(' ') ?? ''}
				/>
				<label for="filter-changed-tags">{m.loose_swift_hare_swap()}</label>
				<input
					id="filter-changed-tags"
					type="text"
					name="changed_tags"
					placeholder={m.petty_fuzzy_fox_ask()}
					value={data.filters.changed_tags?.join(' ') ?? ''}
				/>

				<input class="col-span-full justify-self-start" type="submit" />
			</div>
		</details>
	</form>

	<table class="w-full">
		<tbody>
			{#each data.results?.items ?? [] as r (r.id)}
				<tr
					><td><a href="/revision/{r.id}">#{r.id}</a> </td><td
						>{typeof r.route === 'number' ? routeNames[r.route]() : ''}</td
					><td
						>{#if r.first_entity}<a
								href={buildEntityRoutes(r.first_entity.entity, r.first_entity.id)}
								>{r.first_entity.id}</a
							>{#if r.n_ent > 1}{m.mellow_brave_marten_gather({
									count: r.n_ent - 1
								})}{/if}{/if}</td
					><td
						><Time format="relative" date={r.date} />
						<ParaglideMessage message={m.noble_tidy_boar_lock} inputs={{}}
							>{#snippet content()}<a href="/user/{r.user}">{r.user}</a>{/snippet}</ParaglideMessage
						></td
					></tr
				>
			{/each}
		</tbody>
	</table>

	{#if data.results?.count}
		<Pager
			n_count={data.results.count}
			page_size={data.batch_size}
			base_url={page.url.toString()}
		/>
	{/if}
</Section>
