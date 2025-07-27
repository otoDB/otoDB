<script lang="ts">
	import { page } from '$app/state';
	let { title, children, menuLinks = null } = $props();
</script>

<section
	class="bg-otodb-bg-primary/75 border-otodb-content-primary relative mb-1 mb-4 border px-8 py-6"
>
	{#if menuLinks}
		<menu class="absolute right-0 right-[-1px] bottom-full">
			<ul class="flex list-none gap-2">
				{#each menuLinks as { pathname, title }, i (i)}
					<li
						aria-current={page.url.pathname.endsWith(encodeURI(pathname))}
						class="bg-otodb-bg-primary/75 border-otodb-content-primary border px-2 aria-current:border-b-0"
					>
						<a href="/{pathname}" class="no-underline">{title}</a>
					</li>
				{/each}
			</ul>
		</menu>
	{/if}

	<h1 class="mb-2 text-2xl font-bold">{title}</h1>

	{@render children()}
</section>
