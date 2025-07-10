<script lang="ts">
	import { page } from '$app/state';
	import { m } from '$lib/paraglide/messages.js';
	import { UserLevel } from '$lib/enums';

	let { user, stats } = $props();
</script>

{#snippet link(pathname: string, title: string)}
	<li>
		<a
			href={pathname}
			class="no-underline aria-[current=page]:text-[var(--otodb-fainter-content)]"
			aria-current={page.url.pathname === pathname ? 'page' : undefined}>{title}</a
		>
	</li>
{/snippet}

<nav class="flex w-full min-w-64 flex-col gap-y-2">
	<div class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)]">
		<form target="_self" method="get" action="/work/search" class="flex w-full">
			<input
				type="text"
				name="query"
				placeholder="{m.mean_top_antelope_love()}..."
				class="flex-auto px-2 py-1"
			/>
			<button
				type="submit"
				class="px-1 hover:bg-[var(--otodb-content-bg)]"
				style="border: none !important;"
				aria-label="Search"
			>
				<svg class="h-[16px] w-[16px]">
					<use href="/search.svg#img"></use>
				</svg>
			</button>
		</form>
	</div>

	<div class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2">
		<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
			{m.clean_kind_stork_affirm()}
		</div>
		<ul class="list-none space-y-0.5">
			{@render link('/', m.fine_late_chicken_quiz())}
			{@render link('/work/search', m.grand_merry_fly_succeed())}
			{@render link('/tag/search', m.empty_legal_chicken_taste())}
			{@render link('/list/search', m.stale_loose_squid_cut())}
			{@render link('/work/random', m.fuzzy_chunky_niklas_peek())}
		</ul>
	</div>
	{#if user?.level >= UserLevel.ADMIN}
		<div
			class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2"
		>
			<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
				{m.mellow_pink_starfish_cuddle()}
			</div>
			<ul class="list-none space-y-0.5">
				<li>
					<a href="/admin" data-sveltekit-reload class="no-underline"
						>{m.simple_few_sheep_lend()}</a
					>
				</li>
			</ul>
		</div>
	{/if}
	{#if user?.level >= UserLevel.EDITOR}
		<div
			class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2"
		>
			<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
				{m.these_bold_gorilla_flip()}
			</div>
			<ul class="list-none space-y-0.5">
				{@render link('/tag/alias', m.front_maroon_hamster_urge())}
				{@render link('/work/merge', m.heroic_same_wasp_conquer())}
				{@render link('/work/unbound', m.tense_small_firefox_lock())}
			</ul>
		</div>
	{/if}
	<div class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2">
		<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
			{m.maroon_least_pony_evoke()}
		</div>
		<ul class="list-none space-y-0.5">
			{#if !user}
				{@render link('/login', m.inner_stale_anteater_walk())}
				{@render link('/register', m.blue_whole_camel_type())}
			{:else}
				{@render link('/post/1', m.bald_ideal_gadfly_jest())}
				{@render link('/work/add', m.fluffy_crisp_horse_imagine())}
				{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
				{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
				{@render link(
					`/profile/${user.username}/submissions`,
					m.flaky_gross_marlin_evoke()
				)}
				<li
					aria-current={page.url.pathname === `/logout` ? 'page' : undefined}
					class="mt-5"
				>
					<a
						href="/logout"
						data-sveltekit-preload-data="tap"
						data-sveltekit-reload
						class="no-underline">{m.best_front_swallow_play()}</a
					>
				</li>
			{/if}
		</ul>
	</div>
	<div class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2">
		<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
			{m.white_helpful_lion_rise()}
		</div>
		<div class="flex justify-between">
			<span>{m.grand_merry_fly_succeed()}</span><span>{stats[0]}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.empty_legal_chicken_taste()}</span><span>{stats[1]}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.grand_nice_pony_belong()}</span><span>{stats[2]}</span>
		</div>
		<div class="flex justify-between">
			<span>{m.stale_loose_squid_cut()}</span><span>{stats[3]}</span>
		</div>
	</div>
</nav>
