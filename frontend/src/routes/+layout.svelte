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
	<header class="col-span-2 px-32 py-16">
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
				<span>
					{m.glad_born_mouse_taste()} Alpha
				</span>
				{#if navigating.to}
					<span id="loading-indicator"></span>
				{/if}
				<span>
					<select onchange={(e) => setLocale(e.target.value)} value={getLocale()}>
						<option value="en">{LanguageNames['en']}</option>
						<option value="ja">{LanguageNames['ja']}</option>
						<option value="ko">{LanguageNames['ko']}</option>
						<option value="zh-cn">{LanguageNames['zh-cn']}</option>
					</select>
				</span>
			</footer>
		</div>
	</div>
</div>

<style>
	footer {
		display: flex;
		width: 100%;
		justify-content: space-between;
		margin-bottom: 2rem;
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
