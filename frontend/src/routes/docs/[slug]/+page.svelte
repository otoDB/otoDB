<script lang="ts">
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { languages } from '$lib/enums/language.js';
	import { renderMarkdown } from '$lib/markdown.js';
	import { mount, unmount } from 'svelte';

	let { data } = $props();

	const page = $derived(renderMarkdown(data.content));

	$effect(() => {
		if (page) {
			const tags = Array.from(document.querySelectorAll('.doc-content otodb-worktag'))
				.filter((e) => e.hasAttribute('slug'))
				.map((el) =>
					client
						.GET('/api/tag/tag', {
							fetch,
							params: {
								query: {
									tag_slug: el.getAttribute('slug')!
								}
							}
						})
						.then((r) => mount(WorkTag, { target: el, props: { tag: r.data! } }))
				);
			return () => {
				tags.forEach((p) => p.then(unmount));
			};
		}
	});
</script>

<Section>
	<div class="float-right flex gap-1">
		{#each data.availableLangs as l (l)}
			<a
				href="?lang={l}"
				class="lang-tab"
				aria-current={data.lang === l ? 'page' : undefined}
			>
				{languages[l].name}
			</a>
		{/each}
	</div>
	<div class="doc-content prose prose-neutral prose-sm dark:prose-invert mt-4 max-w-none">
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html page}
	</div>
</Section>

<style>
	.lang-tab {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		text-decoration: none;
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&[aria-current='page'] {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
			pointer-events: none;
		}
	}
</style>
