<script lang="ts">
	import { page } from '$app/state';
	import { base } from '$app/paths';
	import * as m from '$lib/paraglide/messages.js';
	import { UserLevel } from '$lib/enums';

	let { user } = $props();
</script>

{#snippet link(pathname: string, title: string)}
<li aria-current={page.url.pathname === `${base}${pathname}` ? 'page' : undefined}>
	<a href={`${base}${pathname}`}>{title}</a>
</li>
{/snippet}

<header>
	<nav>
		<ul>
			{@render link('/', m.fine_late_chicken_quiz())}
			{@render link('/work/random', 'Random work')}
			<li>
				<form target="_self" method="get" action="{base}/work/search">
					<input type="text" name="query" placeholder="{m.mean_top_antelope_love()}...">
				</form>
			</li>
			{#if user?.level >= UserLevel.MODERATOR}
			<hr>
			{@render link('/tag/alias', 'Alias tags')}
			{@render link('/work/merge', 'Merge works')}
			{@render link('/work/unbound', 'Bind sources')}
			{/if}
			<hr>
			{#if !user}
			{@render link('/login', m.inner_stale_anteater_walk())}
			{@render link('/register', m.blue_whole_camel_type())}
			{:else}
			{@render link('/work/add', 'Add a work...')}
			{@render link(`/profile/${user.username}`, m.petty_basic_sheep_win())}
			{@render link(`/profile/${user.username}/lists`, m.jumpy_honest_mole_exhale())}
			{@render link(`/profile/${user.username}/submissions`, 'My Submissions')}
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
