<script lang="ts">
	import welcome from '$lib/images/svelte-welcome.webp';
	import welcomeFallback from '$lib/images/svelte-welcome.png';

	import * as m from '$lib/paraglide/messages.js';

	import type { PageData } from "./$types";

	export let data: PageData;
</script>

<svelte:head>
	<title>Home</title>
	<meta name="description" content="Svelte demo app" />
</svelte:head>

<section>
	<h1>
		<span class="welcome">
			<picture>
				<source srcset={welcome} type="image/webp" />
				<img src={welcomeFallback} alt="Welcome" />
			</picture>
		</span>

		to the otomad/ytpmv database...
		<br>
		We'll make more progress here soon.
	</h1>
	<p>
		Here is i18n in action:
		{m.hello_world({ name: data.user ? data.user.name : "Guest" })}
		<br>
		Try appending ja, ko, zh-cn to the URL!
	</p>
	<p>
		Here's an API call that will be SSR'd:
	</p>
	{#if data.video.error}
	<div>There was an error: {data.video.error.message}</div>
	{:else if data.video.data}
	<pre><code>{JSON.stringify(data.video.data, undefined, 2)}</code></pre>
	{:else}
	<div>Loading...</div>
	{/if}

</section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}

	h1 {
		width: 100%;
	}

	.welcome {
		display: block;
		position: relative;
		width: 100%;
		height: 0;
		padding: 0 0 calc(100% * 495 / 2048) 0;
	}

	.welcome img {
		position: absolute;
		width: 100%;
		height: 100%;
		top: 0;
		display: block;
	}
</style>
