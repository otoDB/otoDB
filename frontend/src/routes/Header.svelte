<script lang="ts">
	import { page } from '$app/state';
	import { base } from '$app/paths';

	let { user } = $props();
</script>

<header>
	<nav>
		<ul>
			<li aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}>
				<a href="{base}/">Home</a>
			</li>
			<hr>
			{#if !user}
			<li aria-current={page.url.pathname === `${base}/login` ? 'page' : undefined}>
				<a href="{base}/login">Login</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/register` ? 'page' : undefined}>
				<a href="{base}/register">Register</a>
			</li>
			{:else}
			<li aria-current={page.url.pathname === `${base}/profile/${user.user_id}` ? 'page' : undefined}>
				<a href="{base}/profile/{user.user_id}">My Profile</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/profile/${user.user_id}/lists` ? 'page' : undefined}>
				<a href="{base}/profile/{user.user_id}/lists">My Lists</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/logout` ? 'page' : undefined}>
				<a href="{base}/logout" data-sveltekit-preload-data="tap" data-sveltekit-reload>Logout</a>
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
		&> form {
			width: 100%;
			display: flex;
		
			&> input {
				max-width: 4rem;
			}
		}
		&> ul {
			list-style-type: none;
		}
	}
</style>
