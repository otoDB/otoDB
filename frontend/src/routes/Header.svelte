<script lang="ts">
	import { page } from '$app/state';
	import { base } from '$app/paths';

	let { user } = $props();
</script>

<header>
	<nav>
		<ul>
			<li aria-current={page.url.pathname === '/' ? 'page' : undefined}>
				<a href="{base}/">Home</a>
			</li>
			{#if !user}
			<li aria-current={page.url.pathname === '/login' ? 'page' : undefined}>
				<a href="{base}/login">Login</a>
			</li>
			{:else}
			<li aria-current={page.url.pathname === '/logout' ? 'page' : undefined}>
				<a href="{base}/logout">Logout</a>
			</li>
			{/if}
		</ul>
	</nav>
</header>

<style>
	nav {
		display: flex;
		flex-direction: column;
		padding: 2rem 1rem;
		gap: 1rem;
		background-color: var(--otodb-faint-bg);
		border: 1px solid var(--otodb-faint-content);
		max-width: 8rem;
	}

	nav > form {
		width: 100%;
		display: flex;
	}

	nav > form > input {
		max-width: 4rem;
	}
/* 
	nav {
		display: flex;
		justify-content: center;
		--background: rgba(255, 255, 255, 0.7);
	}

	ul {
		position: relative;
		padding: 0;
		margin: 0;
		height: 3em;
		display: flex;
		justify-content: center;
		align-items: center;
		list-style: none;
		background: var(--background);
		background-size: contain;
	}

	li {
		position: relative;
		height: 100%;
	}

	li[aria-current='page']::before {
		--size: 6px;
		content: '';
		width: 0;
		height: 0;
		position: absolute;
		top: 0;
		left: calc(50% - var(--size));
		border: var(--size) solid transparent;
		border-top: var(--size) solid var(--color-theme-1);
	}

	nav a {
		display: flex;
		height: 100%;
		align-items: center;
		padding: 0 0.5rem;
		color: var(--color-text);
		font-weight: 700;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-decoration: none;
		transition: color 0.2s linear;
	}

	a:hover {
		color: var(--color-theme-1);
	} */
</style>
