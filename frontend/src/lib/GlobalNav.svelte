<script lang="ts">
	import { page } from '$app/state';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { m } from '$lib/paraglide/messages.js';
	import { Levels } from '$lib/schema';
	import { clickOutside } from '$lib/ui';

	let { data } = $props();

	let isMobileNavOpen = $state(false);
	function toggleMobileNav() {
		isMobileNavOpen = !isMobileNavOpen;
	}
	function closeMobileNav() {
		isMobileNavOpen = false;
	}

	let search_type = $state('work');
</script>

{#snippet link(pathname: string, title: string)}
	<li>
		<a
			href={pathname}
			class="aria-[current=page]:text-otodb-content-fainter text-xl no-underline md:text-sm"
			aria-current={page.url.pathname === pathname ? 'page' : undefined}
			onclick={closeMobileNav}>{title}</a
		>
	</li>
{/snippet}

<nav
	class={[
		'bg-otodb-bg-faint/90 fixed top-0 left-0 z-2 m-0 flex h-full max-w-[85vw] flex-col gap-y-2 overflow-y-auto p-8 md:visible md:relative md:w-min md:min-w-64 md:bg-transparent md:p-0 md:after:content-none',
		{
			invisible: !isMobileNavOpen
		}
	]}
	use:clickOutside
	onoutclick={() => (isMobileNavOpen = false)}
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

	<div
		class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
	>
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.clean_kind_stork_affirm()}
		</div>
		<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
			{@render link('/', m.fine_late_chicken_quiz())}
			{@render link('/post/2', m.noble_fine_iguana_pull())}
			{@render link('/work', m.grand_merry_fly_succeed())}
			{#if hasUserLevel(data.user?.level, Levels.Member)}
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
	<div
		class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
	>
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.maroon_least_pony_evoke()}
		</div>
		<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
			{#if !data.user}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
				{@render link('/login', m.inner_stale_anteater_walk())}
				{@render link('/register', m.blue_whole_camel_type())}
			{:else}
				{@render link(
					`/profile/${data.user.username}/notifications`,
					m.free_keen_wren_exhale() +
						(data.user.notifs_count > 0
							? m.great_clean_beaver_amuse() +
								m.awful_house_liger_expand({
									content: data.user.notifs_count
								})
							: '')
				)}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
				{@render link('/post/new?category=2', m.bald_ideal_gadfly_jest())}
				{@render link('/upload/add', m.fluffy_crisp_horse_imagine())}
				{@render link(`/profile/${data.user.username}`, m.petty_basic_sheep_win())}
				{@render link(`/profile/${data.user.username}/lists`, m.jumpy_honest_mole_exhale())}
				{@render link(`/request/new`, m.muddy_tough_swan_view())}
				{@render link(
					`/profile/${data.user.username}/submissions`,
					m.flaky_gross_marlin_evoke()
				)}
				<li class="mt-4">
					<form method="POST" action="/logout">
						<button
							type="submit"
							class="w-full cursor-pointer border-none bg-transparent p-0 text-left text-xl text-[inherit] no-underline md:text-sm"
							onclick={closeMobileNav}
						>
							{m.best_front_swallow_play()}
						</button>
					</form>
				</li>
			{/if}
		</ul>
	</div>
	{#if hasUserLevel(data.user?.level, Levels.Editor)}
		<div
			class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
		>
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.these_bold_gorilla_flip()}
			</div>
			<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
				{@render link('/post/4', m.arable_direct_cougar_win())}
				{@render link('/moderation', m.minor_inner_lynx_adapt())}
				{@render link('/tag/alias', m.front_maroon_hamster_urge())}
				{@render link('/work/merge', m.heroic_same_wasp_conquer())}
			</ul>
		</div>
	{/if}
	{#if hasUserLevel(data.user?.level, Levels.Admin)}
		<div
			class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
		>
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.mellow_pink_starfish_cuddle()}
			</div>
			<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
				<li>
					<a href="/admin" data-sveltekit-reload class="no-underline"
						>{m.simple_few_sheep_lend()}</a
					>
				</li>
			</ul>
		</div>
	{/if}
	<div
		class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 hidden md:mt-0 md:block md:border md:px-3 md:py-2"
	>
		<div class="border-otodb-content-faint mb-2 border-b text-xs">
			{m.white_helpful_lion_rise()}
		</div>
		<div class="flex justify-between">
			<span>{m.grand_merry_fly_succeed()}</span><span>{data.stats.works}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.empty_legal_chicken_taste()}</span><span>{data.stats.tags}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.grand_nice_pony_belong()}</span><span>{data.stats.songs}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.stale_loose_squid_cut()}</span><span>{data.stats.lists}</span>
		</div>
	</div>
</nav>
