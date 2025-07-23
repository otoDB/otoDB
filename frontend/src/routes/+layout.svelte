<script lang="ts">
	import '../app.css';
	import { Toaster } from 'svelte-sonner';
	import Header from '../lib/SideNav.svelte';
	import MobileSideNav from '../lib/MobileSideNav.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { navigating } from '$app/state';
	import { clickOutside, get_prefs, set_lang } from '$lib/ui';
	import { LanguageNames, Themes } from '$lib/enums';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { getLocale } from '$lib/paraglide/runtime';

	let { data, children } = $props();

	let isMobileNavOpen = $state(false);
	function toggleMobileNav() {
		isMobileNavOpen = !isMobileNavOpen;
	}
	function closeMobileNav() {
		isMobileNavOpen = false;
	}
</script>

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

<div>
	<div
		class="bg-marker bg-otodb-bg-primary fixed h-lvh w-full {Themes[
			data.user?.prefs?.theme ?? +get_prefs()?.theme
		]}"
	></div>
	<!-- Mobile navigation -->
	<div class="contents md:hidden">
		<!-- Hamburger button -->
		<button
			class={[
				'fixed bottom-[32px] left-[32px] z-[3] h-[64px] w-[64px]',
				{ invisible: isMobileNavOpen }
			]}
			onclick={toggleMobileNav}
		>
			<!-- TODO: Use icon! -->
			<div class="white place-self-center text-2xl">☰</div>
		</button>
		<!-- Cover -->
		<div class={['fixed inset-0 z-[1] bg-black/75', { invisible: !isMobileNavOpen }]}></div>
		<!-- Menu -->
		<div
			use:clickOutside
			onOutclick={closeMobileNav}
			class={[
				'fixed top-0 left-0 z-[2] h-full transition-transform duration-75',
				{
					'-translate-x-full': !isMobileNavOpen
				}
			]}
		>
			<MobileSideNav user={data.user} close={closeMobileNav} className="h-full"
			></MobileSideNav>
		</div>
	</div>

	<header class="relative col-span-2 px-6 py-16 md:px-48">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline!">
				{m.glad_born_mouse_taste()}
			</a>
		</address>
	</header>

	<div class="relative mx-auto flex w-full gap-x-4 px-4">
		<!-- Enough-width navigation -->
		<div class="hidden md:block">
			<Header user={data.user} stats={data.stats}></Header>
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
