<script lang="ts">
	import { page } from '$app/state';
	import DisplayText from './DisplayText.svelte';
	import { m } from './paraglide/messages';
	let { title = undefined, type = undefined, children, menuLinks = null } = $props();
</script>

<section
	class="bg-otodb-bg-faint/75 border-otodb-content-faint relative mb-4 border px-5 pt-3 pb-6"
>
	{#if menuLinks}
		<menu class="absolute -right-px bottom-full">
			<ul class="flex list-none gap-2">
				{#each menuLinks as { pathname, title }, i (i)}
					<li
						aria-current={page.url.pathname.endsWith(encodeURI(pathname))}
						class="bg-otodb-bg-faint/75 border-otodb-content-faint group relative border px-2"
					>
						<a
							href="/{pathname}"
							class="no-underline group-aria-current:pointer-events-none">{title}</a
						>
					</li>
				{/each}
			</ul>
		</menu>
	{/if}

	<h1 class="mb-2 text-2xl font-bold">
		{#if type}{m.mild_loud_shad_enchant({ type, name: '' })}{/if}<DisplayText value={title} />
	</h1>

	{@render children()}
</section>

<style>
	li[aria-current='true'] {
		border-bottom: 0;
		background-color: var(--otodb-color-bg-faint);

		&::after {
			content: '';
			position: absolute;
			bottom: -1px;
			left: -1px;
			right: -1px;
			height: 1px;
			background-color: var(--otodb-color-bg-faint);
		}
	}
</style>
