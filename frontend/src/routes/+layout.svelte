<script lang="ts">
	import { i18n } from '$lib/i18n';
	import { ParaglideJS } from '@inlang/paraglide-sveltekit';
	import Header from './Header.svelte';
	import '../app.css';
	import * as m from '$lib/paraglide/messages.js';
	
	let { data, children } = $props();
</script>

<ParaglideJS {i18n}>
	<span class="absolute top-20 left-40 italic font-mono select-none">
		{m.glad_born_mouse_taste()}
	</span>

	<div class="app">
		<Header user={data.user}></Header>

		<main>
			{@render children()}
		</main>

		<footer>
			{m.glad_born_mouse_taste()} Pre-alpha
		</footer>
	</div>
</ParaglideJS>

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
