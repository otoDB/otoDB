<script lang="ts">
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import * as m from '$lib/paraglide/messages.js';

	let { user } = $props();
</script>

<header>
	<nav>
		<ul>
			<li aria-current={page.url.pathname === `${base}/` ? 'page' : undefined}>
				<a href="{base}/">{m.fine_late_chicken_quiz()}</a>
			</li>
			<li>
				<form tagert="_self" method="get" action="{base}/work/search">
					<input type="text" name="query" placeholder="{m.mean_top_antelope_love()}...">
				</form>
			</li>
			<hr>
			{#if !user}
			<li aria-current={page.url.pathname === `${base}/login` ? 'page' : undefined}>
				<a href="{base}/login">{m.inner_stale_anteater_walk()}</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/register` ? 'page' : undefined}>
				<a href="{base}/register">{m.blue_whole_camel_type()}</a>
			</li>
			{:else}
			<li aria-current={page.url.pathname === `${base}/work/add` ? 'page' : undefined}>
				<a href="{base}/work/add">Add a work...</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/profile/${user.user_id}` ? 'page' : undefined}>
				<a href="{base}/profile/{user.user_id}">{m.petty_basic_sheep_win()}</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/profile/${user.user_id}/lists` ? 'page' : undefined}>
				<a href="{base}/profile/{user.user_id}/lists">{m.jumpy_honest_mole_exhale()}</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/profile/${user.user_id}/submissions` ? 'page' : undefined}>
				<a href="{base}/profile/{user.user_id}/submissions">My Submissions</a>
			</li>
			<li aria-current={page.url.pathname === `${base}/logout` ? 'page' : undefined}>
				<a href="{base}/logout" data-sveltekit-preload-data="tap" data-sveltekit-reload>{m.best_front_swallow_play()}</a>
			</li>
			{/if}
		</ul>
	</nav>
</header>

<style>
	li[aria-current='page'] > a {
		color: var(--otodb-faint-content);
	}
	nav {
		display: flex;
		flex-direction: column;
		padding: 2rem 1rem;
		gap: 1rem;
		background-color: var(--otodb-faint-bg);
		border: 1px solid var(--otodb-faint-content);
		max-width: 8.5rem;
		& form > input {
			width: 100%;
		}
		&> ul {
			list-style-type: none;
			&> li > a {
				text-decoration: none;
			}
			&> hr {
				margin-top: .5rem;
				margin-bottom: .5rem;
			}
		}
	}
</style>
