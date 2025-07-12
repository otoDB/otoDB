<script lang="ts">
	import '../app.css';
	import { getLocale, setLocale } from '$lib/paraglide/runtime';
	import { page } from '$app/state';
	import { m } from '$lib/paraglide/messages.js';
	import { navigating } from '$app/state';
	import { LanguageNames, UserLevel } from '$lib/enums';
	import { clickOutside } from '$lib/ui';

	let { data, children } = $props();

	let isMobileNavOpen = $state(false);
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

<div>
	<header class="col-span-2 px-48 py-16">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline!">
				{m.glad_born_mouse_taste()}
			</a>
		</address>
	</header>

	<div class="contents md:hidden">
		<!-- Hamburger button -->
		<button
			class={[
				'fixed bottom-[32px] left-[32px] z-[3] h-[64px] w-[64px]',
				{
					invisible: isMobileNavOpen
				}
			]}
			onclick={() => (isMobileNavOpen = true)}
		>
			<!-- TODO: Use icon! -->
			<div class="white place-self-center text-2xl">☰</div>
		</button>
		<!-- Menu -->
		<div
			class={[
				'fixed top-0 left-0 z-[2] h-full transition-transform duration-75',
				{
					'-translate-x-full': !isMobileNavOpen
				}
			]}
		></div>
	</div>

	<div class="mx-auto w-full gap-x-4 px-4 md:flex">
		<div
			class={[
				'absolute top-0 left-0 m-0 block w-full md:visible md:relative md:w-max md:after:content-none',
				{
					invisible: !isMobileNavOpen,
					'after:fixed after:top-0 after:z-1 after:size-full after:bg-black after:content-[""]':
						isMobileNavOpen
				}
			]}
		>
			<nav
				class="absolute z-2 flex w-full min-w-64 flex-col gap-y-2 md:relative"
				use:clickOutside
				onOutclick={() => (isMobileNavOpen = false)}
			>
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

				<div
					class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2"
				>
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
				{#if data.user?.level >= UserLevel.ADMIN}
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
				{#if data.user?.level >= UserLevel.EDITOR}
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
				<div
					class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2"
				>
					<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
						{m.maroon_least_pony_evoke()}
					</div>
					<ul class="list-none space-y-0.5">
						{#if !data.user}
							{@render link('/login', m.inner_stale_anteater_walk())}
							{@render link('/register', m.blue_whole_camel_type())}
						{:else}
							{@render link('/post/1', m.bald_ideal_gadfly_jest())}
							{@render link('/work/add', m.fluffy_crisp_horse_imagine())}
							{@render link(
								`/profile/${data.user.username}`,
								m.petty_basic_sheep_win()
							)}
							{@render link(
								`/profile/${data.user.username}/lists`,
								m.jumpy_honest_mole_exhale()
							)}
							{@render link(
								`/profile/${data.user.username}/submissions`,
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
				<div
					class="border border-[var(--otodb-faint-content)] bg-[var(--otodb-faint-bg)] px-3 py-2"
				>
					<div class="border-[var(--otodb-faint-content)2 mb-2 border-b text-xs">
						{m.white_helpful_lion_rise()}
					</div>
					<div class="flex justify-between">
						<span>{m.grand_merry_fly_succeed()}</span><span>{data.stats[0]}</span>
					</div>
					<div class="flex justify-between">
						<span>{m.empty_legal_chicken_taste()}</span><span>{data.stats[1]}</span>
					</div>
					<div class="flex justify-between">
						<span>{m.grand_nice_pony_belong()}</span><span>{data.stats[2]}</span>
					</div>
					<div class="flex justify-between">
						<span>{m.stale_loose_squid_cut()}</span><span>{data.stats[3]}</span>
					</div>
				</div>
			</nav>
		</div>
		<div class="flex-grow">
			<main>
				{@render children()}
			</main>
			<footer>
				<div class="footer-left">
					{#if navigating.to}
						<span id="loading-indicator"></span>
					{/if}
				</div>
				<div class="footer-center">
					<span>
						{m.glad_born_mouse_taste()} Alpha
					</span>
					<div class="social-links">
						<a href="mailto:contact@otodb.net">contact@otodb.net</a>
						/
						<a href="irc://irc.rizon.net/#otodb">#otodb @ Rizon</a>
					</div>
				</div>
				<div class="footer-right">
					<select onchange={(e) => setLocale(e.target.value)} value={getLocale()}>
						<option value="en">{LanguageNames['en']}</option>
						<option value="ja">{LanguageNames['ja']}</option>
						<option value="ko">{LanguageNames['ko']}</option>
						<option value="zh-cn">{LanguageNames['zh-cn']}</option>
					</select>
				</div>
			</footer>
		</div>
	</div>
</div>

<style>
	footer {
		display: flex;
		width: 100%;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 2rem;
	}

	.footer-left,
	.footer-right {
		flex: 1;
	}

	.footer-center {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.footer-right {
		display: flex;
		justify-content: flex-end;
	}

	.social-links a {
		border-bottom: 1px dotted var(--otodb-content-color);
		text-decoration: none;
		color: inherit;
	}

	.social-links a:hover {
		opacity: 0.7;
	}

	@keyframes loading-dot {
		0% {
			content: '.';
		}
		33% {
			content: '..';
		}
		66% {
			content: '...';
		}
		100% {
			content: '.';
		}
	}
	#loading-indicator::after {
		content: '.';
		animation: loading-dot 0.4s infinite;
	}
</style>
