<script lang="ts">
	import { page } from '$app/state';
	let { title, children, menuLinks = null } = $props();
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
						class="bg-otodb-bg-faint/75 border-otodb-content-faint border px-2 aria-current:border-b-0"
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
