<script lang="ts">
	import { i18n } from '$lib/i18n';
	import { ParaglideJS } from '@inlang/paraglide-sveltekit';
	import Header from './Header.svelte';
	import '../app.css';
	import { setToken } from '$lib/api.js';
	
	let { data, children } = $props();

	if (data?.csrf)
		setToken(data.csrf)
</script>

<ParaglideJS {i18n}>
	<div class="app">
		<Header user={data.user}></Header>

		<main>
			{@render children()}
		</main>

		<footer>
			the otomad/ytpmv database
		</footer>
	</div>
</ParaglideJS>

<style>
.app {
	display: grid;
	grid-template-columns: max-content 1fr;
	align-items: flex-start;
	gap: 1rem;
}

main {
	margin: 0 auto;
	width: 100%;
	min-height: 15rem;
/*	
	& > menu {
		display: flex;
		margin: 0;
		margin-top: -.5rem;
		gap: .3rem;
		& a {
			background-color: var(--otodb-faint-bg);
			  border: 1px solid var(--otodb-faint-content);
			border-bottom: none;
			padding: .2rem .2rem 0 .2rem;
		}
		& > a.current::after {
			content: '';
			width: 100%;
			height: 2px;
			background-color:  var(--otodb-faint-bg);
			display: block;
			position: relative;
			bottom: -.1rem;
			width: calc(100% + .4rem);
			left: -.2rem;
		}
	}
	
	& > menu.right {
		margin-left: auto;
		margin-right: 0;
		width: max-content;
	} */
}

footer {
	grid-column: 2;
}
</style>
