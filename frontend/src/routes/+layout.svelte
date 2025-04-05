<script lang="ts">
	import '../app.css';
	import Header from '../lib/SideNav.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data, children } = $props();
</script>

<div>
	<header class="col-span-2 px-32 py-16">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline">
				{m.glad_born_mouse_taste()}
			</a>
		</address>
	</header>

	<div class="mx-auto flex w-full gap-x-4 px-4">
		<div class="w-[256px] flex-shrink-0">
			<Header user={data.user}></Header>
		</div>
		<div class="flex-grow">
			<main>
				{@render children()}
			</main>
			<footer>
				{m.glad_born_mouse_taste()} Pre-alpha
			</footer>
		</div>
	</div>
</div>
