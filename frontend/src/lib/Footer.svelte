<script lang="ts">
	import { navigating } from '$app/state';
	import { PUBLIC_OTODB_HASH } from '$env/static/public';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { languages } from '$lib/enums/language';
	import { currentVersion, versions } from '$lib/enums/version';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { set_lang } from '$lib/ui';
	import type { ClassValue } from 'svelte/elements';

	let {
		user,
		...props
	}: {
		user: null | { username: string };
		class?: ClassValue;
	} = $props();
</script>

<footer class={props.class}>
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
			{versions[currentVersion].name}
			{#if PUBLIC_OTODB_HASH}
				- <a href="https://github.com/otoDB/otoDB">{PUBLIC_OTODB_HASH}</a>{/if}
		</span>
		<div class="social-links">
			<a href="https://discord.com/invite/YRAvgAYHkh">Discord</a>
			/
			<a href="https://twitter.com/otoDBnet">Twitter</a>
			/
			<a href="irc://irc.rizon.net/otodb">#otodb @ Rizon</a>
			/
			<a href="mailto:contact@otodb.net">contact@otodb.net</a>
		</div>
	</div>

	<div class="footer-right">
		<ConnectionFavicon type="Website" class="size-4" />
		<select
			onchange={(e) => {
				set_lang(e.currentTarget.value as (typeof locales)[number], !!user);
			}}
			value={getLocale()}
		>
			{#each locales as l (l)}
				<option value={l}>{languages[l].name}</option>
			{/each}
		</select>
	</div>
</footer>

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
