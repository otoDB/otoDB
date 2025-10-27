<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { Toaster } from 'svelte-sonner';
	import { m } from '$lib/paraglide/messages.js';
	import { navigating } from '$app/state';
	import { clickOutside, current_version, get_prefs, isFormDirty, set_lang } from '$lib/ui';
	import { LanguageNames, Themes, UserLevel } from '$lib/enums';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { beforeNavigate } from '$app/navigation';
	import * as env from '$env/static/public';

	let { data, children } = $props();

	let isMobileNavOpen = $state(false);
	function toggleMobileNav() {
		isMobileNavOpen = !isMobileNavOpen;
	}
	function closeMobileNav() {
		isMobileNavOpen = false;
	}
	beforeNavigate(({ cancel, type }) => {
		if (
			type !== 'form' &&
			type !== 'goto' &&
			Array.from(document.querySelectorAll('form')).some(isFormDirty)
		)
			if (!confirm(m.raw_actual_mallard_exhale())) cancel();
	});

	let search_type = $state('work');

	const theme = Themes[data.user?.prefs?.theme ?? +get_prefs()?.theme];
</script>

<a href="#content" class="absolute z-50 transform-[translateY(-100%)] focus:transform-none">
	{m.round_extra_impala_fry()}
</a>

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

<div class="text-otodb-content-primary overflow-auto {theme}">
	<div class="bg-marker bg-otodb-bg-primary fixed h-lvh w-full"></div>
	<div class="contents md:hidden">
		<!-- Hamburger button -->
		<button
			class={[
				'bg-otodb-bg-primary/90 fixed bottom-[32px] left-[32px] z-[3] h-12 w-12',
				{ invisible: isMobileNavOpen }
			]}
			onclick={toggleMobileNav}
		>
			<div class="white place-self-center text-2xl">☰</div>
		</button>
	</div>
	<Toaster
		expand={true}
		position="bottom-right"
		toastOptions={{
			unstyled: true,
			classes: {
				toast: 'bg-otodb-bg-faint text-otodb-content-color flex p-2 gap-3 border-otodb-fainter-content border'
			}
		}}
	/>
	<header class="relative col-span-2 px-6 py-16 md:px-48">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline!">
				{m.mild_loud_shad_enchant({ type: 'otoDB', name: m.glad_born_mouse_taste() })}
			</a>
		</address>
	</header>

	<div class="relative mx-auto w-full gap-x-4 px-4 md:flex">
		<div
			class={[
				'fixed top-0 left-0 z-2 size-full md:pointer-events-auto md:relative md:size-auto md:bg-transparent',
				isMobileNavOpen ? 'bg-otodb-bg-primary/90' : 'pointer-events-none bg-transparent'
			]}
		>
			<nav
				class={[
					'bg-otodb-bg-faint/90 fixed top-0 left-0 z-2 m-0 flex h-full max-w-[85vw] flex-col gap-y-2 overflow-y-auto p-8 md:visible md:relative md:w-min md:min-w-64 md:bg-transparent md:p-0 md:after:content-none',
					{
						invisible: !isMobileNavOpen
					}
				]}
				use:clickOutside
				onOutclick={() => (isMobileNavOpen = false)}
			>
				<form
					target="_self"
					method="get"
					action="/{search_type}/search"
					class="flex w-full"
				>
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
						{@render link('/work/search', m.grand_merry_fly_succeed())}
						{#if data.user?.level >= UserLevel.MEMBER}
							{@render link('/work/tags_needed', `> ${m.spry_late_kudu_assure()}`)}
						{/if}
						{@render link('/tag/search', m.empty_legal_chicken_taste())}
						{@render link('/song/search', m.grand_nice_pony_belong())}
						{@render link('/list/search', m.stale_loose_squid_cut())}
						{@render link('/post/overview', m.just_salty_anaconda_nourish())}
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
							{@render link(`/settings`, m.orange_born_seal_ascend())}
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
							{@render link(`/request/new`, m.muddy_tough_swan_view())}
							{@render link(
								`/profile/${data.user.username}/submissions`,
								m.flaky_gross_marlin_evoke()
							)}
							<li
								aria-current={page.url.pathname === `/logout` ? 'page' : undefined}
								class="mt-4"
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
				{#if data.user?.level >= UserLevel.EDITOR}
					<div
						class="md:border-otodb-content-faint md:bg-otodb-bg-faint/75 mt-8 md:mt-0 md:border md:px-3 md:py-2"
					>
						<div class="border-otodb-content-faint mb-2 border-b text-xs">
							{m.these_bold_gorilla_flip()}
						</div>
						<ul class="mt-4 list-none space-y-4 md:mt-0 md:space-y-0.5">
							{@render link('/post/4', m.arable_direct_cougar_win())}
							{@render link('/work/unbound', m.tense_small_firefox_lock())}
							{@render link('/tag/alias', m.front_maroon_hamster_urge())}
							{@render link('/work/merge', m.heroic_same_wasp_conquer())}
						</ul>
					</div>
				{/if}
				{#if data.user?.level >= UserLevel.ADMIN}
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
		<div class="grow">
			<main id="content">
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
						{m.mild_loud_shad_enchant({
							type: 'otoDB',
							name: m.glad_born_mouse_taste()
						})}
						{current_version}
						{#if env.PUBLIC_OTODB_HASH}
							- {env.PUBLIC_OTODB_HASH}{/if}
					</span>
					<div class="social-links">
						<a href="https://discord.com/invite/YRAvgAYHkh">Discord</a>
						/
						<a href="https://twitter.com/otoDBnet">Twitter</a>
						/
						<a href="irc://irc.rizon.net/#otodb">#otodb @ Rizon</a>
						/
						<a href="mailto:contact@otodb.net">contact@otodb.net</a>
					</div>
				</div>
				<div class="footer-right">
					<ConnectionFavicon type="Website" class="size-4" />
					<select
						onchange={(e) => set_lang(e.target.value, !!data.user)}
						value={getLocale()}
					>
						{#each locales as l, i (i)}
							<option value={l}>{LanguageNames[l]}</option>
						{/each}
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
		flex: 3;
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
		border-bottom: 1px dotted var(--otodb-color-content-primary);
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
