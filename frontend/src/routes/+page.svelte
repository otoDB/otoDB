<script lang="ts">
	import { setLocale } from '$lib/paraglide/runtime';
	import { m } from '$lib/paraglide/messages.js';
	
	import Section from '$lib/Section.svelte';
	import { base } from '$app/paths';

    let { data } = $props();
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
		<button onclick={() => setLocale('en')}>English</button>
		<button onclick={() => setLocale('ja')}>日本語</button>
		<button onclick={() => setLocale('ko')}>한국인</button>
		<button onclick={() => setLocale('zh-cn')}>简体中文</button>
	</p>

	<div>
		<h2>Random work: <a href="{base}/work/{data.work.data.id}">{data.work.data.title}</a> </h2><img style="width:25rem;" src={data.work.data.thumbnail} alt={data.work.data.title}/>
	</div>
</Section>

<style>
</style>
