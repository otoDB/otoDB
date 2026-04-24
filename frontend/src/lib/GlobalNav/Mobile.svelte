<script lang="ts">
	import { page } from '$app/state';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { m } from '$lib/paraglide/messages.js';
	import { Levels, type components } from '$lib/schema';
	import type { ClassValue } from 'svelte/elements';

	let {
		user,
		stats,
		...props
	}: {
		user: null | {
			username: string;
			level: components['schemas']['Levels'];
			notifs_count: number;
			notifs_nonsub_count: number;
		};
		stats: {
			works: number;
			tags: number;
			songs: number;
			lists: number;
		};
		class?: ClassValue;
		close: () => void;
	} = $props();

	let search_type = $state('work');
</script>

{#snippet link(pathname: string, title: string)}
	<li>
		<a
			href={pathname}
			class="aria-[current=page]:text-otodb-content-fainter text-xl no-underline"
			aria-current={page.url.pathname === pathname ? 'page' : undefined}
			onclick={() => close()}>{title}</a
		>
	</li>
{/snippet}

<nav
	class={[props.class, 'bg-otodb-bg-faint/90 z-2 m-0 flex flex-col gap-y-2 overflow-y-auto p-8']}
>
	<form target="_self" method="get" action="/{search_type}" class="flex w-full">
		<select bind:value={search_type} class="bg-otodb-bg-faint/75 pl-1">
			<option value="work">{m.grand_merry_fly_succeed()}</option>
			<option value="tag">{m.empty_legal_chicken_taste()}</option>
			<option value="list">{m.stale_loose_squid_cut()}</option>
		</select>
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			class="bg-otodb-bg-faint/75 border-otodb-content-faint w-[inherit] px-2 py-1"
		/>
		<button
			type="submit"
			aria-label="Search"
			class="bg-otodb-bg-faint/75 hover:bg-otodb-bg-fainter/75 px-2"
		>
			<svg class="h-[16px] w-[16px]">
				<use href="/search.svg#img"></use>
			</svg>
		</button>
	</form>

	<div class="mt-8">
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.clean_kind_stork_affirm()}
		</div>
		<ul class="mt-4 list-none space-y-4">
			{@render link('/', m.fine_late_chicken_quiz())}
			{@render link('/post/2', m.noble_fine_iguana_pull())}
			{@render link('/work', m.grand_merry_fly_succeed())}
			{#if hasUserLevel(user?.level, Levels.Member)}
				{@render link('/work/tags_needed', `> ${m.spry_late_kudu_assure()}`)}
			{/if}
			{@render link('/tag', m.empty_legal_chicken_taste())}
			{@render link('/song', m.grand_nice_pony_belong())}
			{@render link('/song_attribute', `> ${m.dull_plain_angelfish_cuddle()}`)}
			{@render link('/list', m.stale_loose_squid_cut())}
			{@render link('/post/overview', m.just_salty_anaconda_nourish())}
			{@render link('/comments', m.same_broad_haddock_pinch())}
			{@render link('/profile', m.bright_nimble_eagle_glide())}
			{@render link('/post/3', 'FAQ')}
			{@render link('/work/random', m.fuzzy_chunky_niklas_peek())}
		</ul>
	</div>
	<div class="mt-8">
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.maroon_least_pony_evoke()}
			{#if user}
				<a
					href={`/profile/${user.username}/notifications`}
					title={m.free_keen_wren_exhale()}
					class="relative -top-0.5 no-underline"
				>
					{#if user.notifs_nonsub_count > 0}({user.notifs_nonsub_count}){/if}
					<span
						class={[
							'text-transparent',
							user.notifs_count > 0
								? '[text-shadow:0_0_var(--otodb-color-content-fainter)]'
								: 'opacity-25 [text-shadow:0_0_var(--otodb-color-content-primary)]'
						]}>🔔</span
					>
				</a>
			{/if}
		</div>
		<ul class="mt-4 list-none space-y-4">
			{#if !user}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
				{@render link('/login', m.inner_stale_anteater_walk())}
				{@render link('/register', m.blue_whole_camel_type())}
			{:else}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
				{@render link('/post/new?category=2', m.bald_ideal_gadfly_jest())}
				{@render link('/upload/add', m.fluffy_crisp_horse_imagine())}
				{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
				{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
				{@render link(`/request/new`, m.muddy_tough_swan_view())}
				{@render link(
					`/profile/${user.username}/submissions`,
					m.flaky_gross_marlin_evoke()
				)}
				<li class="mt-4">
					<form method="POST" action="/logout">
						<button
							type="submit"
							class="w-full cursor-pointer border-none bg-transparent p-0 text-left text-xl text-[inherit] no-underline"
							onclick={() => close()}
						>
							{m.best_front_swallow_play()}
						</button>
					</form>
				</li>
			{/if}
		</ul>
	</div>
	{#if hasUserLevel(user?.level, Levels.Editor)}
		<div class="mt-8">
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.these_bold_gorilla_flip()}
			</div>
			<ul class="mt-4 list-none space-y-4">
				{@render link('/moderation', m.minor_inner_lynx_adapt())}
				{@render link('/tag/alias', m.front_maroon_hamster_urge())}
				{@render link('/work/merge', m.heroic_same_wasp_conquer())}
				{@render link('/post/4', m.arable_direct_cougar_win())}
			</ul>
		</div>
	{/if}
	{#if hasUserLevel(user?.level, Levels.Admin)}
		<div class="mt-8">
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.mellow_pink_starfish_cuddle()}
			</div>
			<ul class="mt-4 list-none space-y-4">
				<li>
					<a href="/admin" data-sveltekit-reload class="no-underline"
						>{m.simple_few_sheep_lend()}</a
					>
				</li>
			</ul>
		</div>
	{/if}
	<div class="mt-8 hidden">
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.white_helpful_lion_rise()}
		</div>
		<div class="flex justify-between">
			<span>{m.grand_merry_fly_succeed()}</span><span>{stats.works}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.empty_legal_chicken_taste()}</span><span>{stats.tags}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.grand_nice_pony_belong()}</span><span>{stats.songs}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.stale_loose_squid_cut()}</span><span>{stats.lists}</span>
		</div>
	</div>
</nav>
