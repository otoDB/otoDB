<script lang="ts">
	import '../app.css';
	import { getLocale, setLocale } from '$lib/paraglide/runtime';
	import Header from '../lib/SideNav.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { navigating } from '$app/state';
	import { LanguageNames } from '$lib/enums';

	let { data, children } = $props();
</script>

<div>
	<header class="col-span-2 px-48 py-16">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline!">
				{m.glad_born_mouse_taste()}
			</a>
		</address>
	</header>

	<div class="mx-auto flex w-full gap-x-4 px-4">
		<div class="flex-shrink-0">
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
