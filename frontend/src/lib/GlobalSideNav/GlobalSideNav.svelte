<script lang="ts">
	import { page } from '$app/state';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { m } from '$lib/paraglide/messages.js';
	import { Levels } from '$lib/schema';

	let {
		user,
		stats
	}: {
		user: {
			level: Levels;
			username: string;
			notifs_nonsub_count: number;
			notifs_count: number;
		} | null;
		stats: {
			works: number;
			tags: number;
			songs: number;
			lists: number;
		};
	} = $props();

	let search_type = $state<'work' | 'tag' | 'list'>('work');

	let isSidebarOpen = $state(false);
	const closeSidebar = () => {
		isSidebarOpen = false;
	};
</script>

{#snippet link(pathname: string, title: string)}
	<li>
		<a
			href={pathname}
			class="aria-[current=page]:text-otodb-content-fainter text-xl no-underline md:text-sm"
			aria-current={page.url.pathname === pathname ? 'page' : undefined}
			onclick={closeSidebar}>{title}</a
		>
	</li>
{/snippet}

<input type="checkbox" class="peer hidden" bind:checked={isSidebarOpen} id="sidebar-open" />
<label
	for="sidebar-open"
	class="border-otodb-content-faint/90 bg-otodb-bg-primary/90 fixed bottom-[32px] left-[32px] z-2 flex h-12 w-12 cursor-pointer border peer-checked:top-0 peer-checked:left-0 peer-checked:h-full peer-checked:w-full peer-checked:cursor-auto md:hidden"
	aria-label={m.clean_kind_stork_affirm()}
>
	<span class="icon-[gravity-ui--bars] m-auto size-6" aria-hidden="true"></span>
</label>
<nav
	class="bg-otodb-bg-faint/90 fixed top-0 left-0 z-3 m-0 hidden h-full max-w-[85vw] flex-col gap-y-2 overflow-y-auto p-8 peer-checked:flex md:visible md:relative md:flex md:w-min md:min-w-64 md:bg-transparent md:p-0 md:after:content-none"
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
			<span class="icon-[gravity-ui--magnifier]" aria-hidden="true"></span>
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
			{@render link('/wiki/about', m.noble_fine_iguana_pull())}
			{@render link('/work', m.grand_merry_fly_succeed())}
			{@render link('/upload/add', `> ${m.fluffy_crisp_horse_imagine()}`)}
			{@render link('/tag', m.empty_legal_chicken_taste())}
			{@render link('/song', m.grand_nice_pony_belong())}
			{@render link('/song_attribute', `> ${m.dull_plain_angelfish_cuddle()}`)}
			{@render link('/wiki', `${m.curly_zesty_pelican_aim()}`)}
			{@render link('/list', m.stale_loose_squid_cut())}
			{@render link('/thread/overview', m.just_salty_anaconda_nourish())}
			{@render link('/comments', m.same_broad_haddock_pinch())}
			{@render link('/profile', m.bright_nimble_eagle_glide())}
			{@render link('/wiki/faq', 'FAQ')}
			{@render link('/work/random', m.fuzzy_chunky_niklas_peek())}
		</ul>
	</div>
	<div
		class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
	>
		<div class="border-otodb-content-faint mb-2 flex items-center justify-between border-b text-xs">
			<span>{m.maroon_least_pony_evoke()}</span>
			{#if user}
				<a
					href={`/profile/${user.username}/notifications`}
					title={m.free_keen_wren_exhale()}
					class="relative -top-0.5 inline-flex no-underline"
					onclick={closeSidebar}
				>
					{#if user.notifs_nonsub_count > 0}({user.notifs_nonsub_count}){/if}
					<span
						aria-hidden="true"
						class={[
							'text-otodb-content-fainter ml-1 size-4',
							user.notifs_count > 0 ? 'icon-[gravity-ui--bell-fill]' : 'icon-[gravity-ui--bell]'
						]}
					></span>
				</a>
			{/if}
		</div>
		<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
			{#if !user}
				{@render link('/login', m.inner_stale_anteater_walk())}
				{@render link('/register', m.blue_whole_camel_type())}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
			{:else}
				{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
				{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
				{@render link(`/profile/${user.username}/submissions`, m.flaky_gross_marlin_evoke())}
				{@render link(`/request/new`, m.muddy_tough_swan_view())}
				{@render link(`/settings`, m.orange_born_seal_ascend())}
				<li class="mt-4">
					<form method="POST" action="/logout">
						<button
							type="submit"
							class="w-full cursor-pointer border-none bg-transparent p-0 text-left text-xl text-[inherit] no-underline md:text-sm"
							onclick={closeSidebar}
						>
							{m.best_front_swallow_play()}
						</button>
					</form>
				</li>
			{/if}
		</ul>
	</div>
	{#if hasUserLevel(user?.level, Levels.Editor)}
		<div
			class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
		>
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.these_bold_gorilla_flip()}
			</div>
			<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
				{@render link('/moderation', m.minor_inner_lynx_adapt())}
				{@render link('/tag/alias', m.front_maroon_hamster_urge())}
				{@render link('/work/merge', m.heroic_same_wasp_conquer())}
				{@render link('/wiki/editing_guidelines', m.arable_direct_cougar_win())}
			</ul>
		</div>
	{/if}
	{#if hasUserLevel(user?.level, Levels.Admin)}
		<div
			class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
		>
			<div class="border-otodb-content-faint mb-2 border-b text-xs">
				{m.mellow_pink_starfish_cuddle()}
			</div>
			<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
				<li>
					<a href="/admin" data-sveltekit-reload class="no-underline">{m.simple_few_sheep_lend()}</a
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

<style>
	input[type='checkbox']:checked ~ label > span {
		display: none;
	}
</style>
