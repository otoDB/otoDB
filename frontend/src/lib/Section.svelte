<script lang="ts">
	import { page } from '$app/state';
	import DisplayText from '$lib/DisplayText.svelte';
	import { m } from '$lib/paraglide/messages';
	let {
		title = undefined,
		type = undefined,
		children,
		menuLinks = null,
		href = undefined
	} = $props();
</script>

{#snippet render_title()}
	{#if typeof title === 'function'}
		{@render title()}
	{:else}
		<DisplayText value={title} />
	{/if}
{/snippet}

<div class="relative mb-4">
	{#if menuLinks}
		<menu class="absolute -right-px bottom-[calc(100%-1px)] z-1">
			<ul class="flex list-none gap-2">
				{#each menuLinks as { pathname, title }, i (i)}
					<li
						aria-current={page.url.pathname.endsWith(encodeURI(pathname))}
						class="bg-otodb-bg-faint/75 border-otodb-content-faint group relative border px-2"
					>
						<a href="/{pathname}" class="no-underline group-aria-current:pointer-events-none"
							>{title}</a
						>
					</li>
				{/each}
			</ul>
		</menu>
	{/if}

	<section
		class="bg-otodb-bg-faint/75 border-otodb-content-faint relative w-fit min-w-full border px-5 pt-3 pb-6"
	>
		<h1 class="mb-2 text-2xl font-bold">
			{#if href}
				<a {href}>
					{#if type}{m.mild_loud_shad_enchant({
							type,
							name: ''
						})}{/if}{@render render_title()}
				</a>
			{:else}
				{#if type}{m.mild_loud_shad_enchant({ type, name: '' })}{/if}{@render render_title()}
			{/if}
		</h1>

		{@render children()}
	</section>
</div>

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
