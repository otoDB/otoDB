<script lang="ts">
	import { page } from '$app/state';
	let { title, children, menuLinks = null } = $props();
</script>

<section>
	{#if menuLinks}
		<menu>
			<ul>
				{#each menuLinks as { pathname, title }, i (i)}
					<li aria-current={page.url.pathname.endsWith(encodeURI(pathname))}>
						<a href="/{pathname}">{title}</a>
					</li>
				{/each}
			</ul>
		</menu>
	{/if}

	<h1>{title}</h1>
	{@render children()}
</section>

<style>
	section {
		background-color: var(--otodb-faint-bg);
		border: 1px solid var(--otodb-faint-content);
		padding: 0 1rem 1rem 1rem;
		margin-bottom: 1rem;
		position: relative;
		& > h1 {
			font-size: x-large;
			font-weight: 600;
			text-align: initial;
		}
		&::after {
			/* Clearfix */
			content: '';
			display: block;
			clear: both;
		}
	}
	menu {
		position: absolute;
		bottom: 100%;
		right: -1px;
		z-index: 1;
		& > ul {
			display: flex;
			gap: 0.3rem;
			width: max-content;
			list-style: none;
			flex-direction: row;
			& > li {
				background-color: var(--otodb-faint-bg);
				border: 1px solid var(--otodb-faint-content);
				padding-left: 0.2rem;
				padding-right: 0.2rem;
				&[aria-current='true'] {
					border-bottom: none;
					pointer-events: none;
				}
			}
		}
	}
</style>
