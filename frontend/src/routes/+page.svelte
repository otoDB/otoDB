<script lang="ts">
	import type { AvailableLanguageTag } from '$lib/paraglide/runtime';
	import { i18n } from '$lib/i18n';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import * as m from '$lib/paraglide/messages.js';
	
	import Section from './Section.svelte';
	import { base } from '$app/paths';

    let { data } = $props();

	function switchToLanguage(newLanguage: AvailableLanguageTag) {
		const canonicalPath = i18n.route(page.url.pathname);
		const localisedPath = i18n.resolveRoute(canonicalPath, newLanguage);
		goto(localisedPath);
	}
</script>

<svelte:head>
	<title>{m.fine_late_chicken_quiz()}</title>
	<meta name="description" content="the otomad/ytpmv database" />
</svelte:head>

<Section title={m.fine_late_chicken_quiz()}>
	<p>
		Welcome to the otomad/ytpmv database... We'll make more progress here soon.
	</p>
	<p>
		Here is i18n in action:
		{m.hello_world({ name: data.user ? data.user.username : "Guest" })}
		<br>
		Click here (look at the URL bar!):
		<button onclick={() => switchToLanguage('en')}>English</button>
		<button onclick={() => switchToLanguage('ja')}>日本語</button>
		<button onclick={() => switchToLanguage('ko')}>한국인</button>
		<button onclick={() => switchToLanguage('zh-cn')}>简体中文</button>
	</p>

	{#if data.work.error}
	<div>There was an error: {data.work.error.message}</div>
	{:else if data.work.data}
	<div>
		<h2>Random work: <a href="{base}/work/{data.work.data.id}">{data.work.data.title}</a> </h2><img style="width:25rem;" src="{ data.work.data.thumbnail }" alt="{ data.work.data.title }"/>
	</div>
	{:else}
	<div>Loading...</div>
	{/if}
</Section>

<style>
</style>
