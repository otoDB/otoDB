<script lang="ts">
	import { page } from '$app/state';
	import { m } from '$lib/paraglide/messages.js';
	import { UserLevel } from '$lib/enums';

	let { user, stats } = $props();
</script>

{#snippet link(pathname: string, title: string)}
	<li aria-current={page.url.pathname === pathname ? 'page' : undefined}>
		<a href={pathname}>{title}</a>
	</li>
{/snippet}

<nav class="w-full">
	<ul>
		<li>{m.clean_kind_stork_affirm()}</li>
		{@render link('/', m.fine_late_chicken_quiz())}
		{@render link('/work/search', m.grand_merry_fly_succeed())}
		{@render link('/tag/search', m.empty_legal_chicken_taste())}
		{@render link('/list/search', m.stale_loose_squid_cut())}
		{@render link('/work/random', m.fuzzy_chunky_niklas_peek())}
		<li>
			<form target="_self" method="get" action="/work/search">
				<input type="text" name="query" placeholder="{m.mean_top_antelope_love()}..." />
			</form>
		</li>
	</ul>
	{#if user?.level >= UserLevel.ADMIN}
		<ul>
			<li>{m.mellow_pink_starfish_cuddle()}</li>
			<li>
				<a href="/admin" data-sveltekit-reload>{m.simple_few_sheep_lend()}</a>
			</li>
		</ul>
	{/if}
	{#if user?.level >= UserLevel.MODERATOR}
		<ul>
			<li>{m.these_bold_gorilla_flip()}</li>
			{@render link('/tag/alias', m.front_maroon_hamster_urge())}
			{@render link('/work/merge', m.heroic_same_wasp_conquer())}
			{@render link('/work/unbound', m.tense_small_firefox_lock())}
		</ul>
	{/if}
	<ul>
		<li>{m.maroon_least_pony_evoke()}</li>
		{#if !user}
			{@render link('/login', m.inner_stale_anteater_walk())}
			{@render link('/register', m.blue_whole_camel_type())}
		{:else}
			{@render link('/post/1', m.bald_ideal_gadfly_jest())}
			{@render link('/work/add', m.fluffy_crisp_horse_imagine())}
			{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
			{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
			{@render link(`/profile/${user.username}/submissions`, m.flaky_gross_marlin_evoke())}
			<li aria-current={page.url.pathname === `/logout` ? 'page' : undefined} class="mt-5">
				<a href="/logout" data-sveltekit-preload-data="tap" data-sveltekit-reload
					>{m.best_front_swallow_play()}</a
				>
			</li>
		{/if}
	</ul>
	<ul>
		<li>{m.white_helpful_lion_rise()}</li>
		<li class="flex justify-between">
			<span>{m.grand_merry_fly_succeed()}</span><span>{stats[0]}</span>
		</li>
		<li class="flex justify-between">
			<span>{m.empty_legal_chicken_taste()}</span><span>{stats[1]}</span>
		</li>
		<li class="flex justify-between">
			<span>{m.grand_nice_pony_belong()}</span><span>{stats[2]}</span>
		</li>
		<li class="flex justify-between">
			<span>{m.stale_loose_squid_cut()}</span><span>{stats[3]}</span>
		</li>
	</ul>
</nav>

<style>
	li[aria-current='page'] > a {
		color: var(--otodb-fainter-content);
	}
	nav {
		display: flex;
		flex-direction: column;
		gap: 1rem;
		& form > input {
			width: 100%;
		}
		& > ul {
			list-style-type: none;
			& > li:first-child {
				border-bottom: 1px solid var(--otodb-faint-content);
				margin-bottom: 0.5rem;
				font-size: smaller;
			}
			& > li > a {
				text-decoration: none;
			}
			padding: 0.25rem 0.5rem 0.5rem 0.5rem;
			background-color: var(--otodb-faint-bg);
			border: 1px solid var(--otodb-faint-content);
		}
	}
</style>
