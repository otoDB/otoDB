<script lang="ts">
	import Header from './Header.svelte';
	import '../app.css';
	import { m } from '$lib/paraglide/messages.js';

	let { data, children } = $props();
</script>

<div class="app">
	<address class="absolute top-20 left-40 font-mono italic select-none">
		{m.glad_born_mouse_taste()}
	</address>

	<Header user={data.user}></Header>

	<main>
		{@render children()}
	</main>

	<footer>
		{m.glad_born_mouse_taste()} Pre-alpha
	</footer>
</div>

<style>
	.app {
		display: grid;
		grid-template-columns: max-content 1fr;
		align-items: flex-start;
		column-gap: 1rem;
	}

	main {
		margin: 0 auto;
		width: 100%;
	}

	footer {
		grid-column: 2;
	}
</style>
