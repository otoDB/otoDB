<script lang="ts">
	import CommentTree from '$lib/CommentTree.svelte';
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { m } from '$lib/paraglide/messages.js';
	import { mount, onMount } from 'svelte';

	let { data } = $props();
	let page = $derived.by(() => {
		return data.post.post_rendered.replaceAll(
			/&lt;otodb-worktag\s*slug="(.+)"\s*\/&gt;/g,
			'<otodb-worktag data-slug="$1" />'
		);
	});
	onMount(() => {
		document.querySelectorAll('.post-content otodb-worktag').forEach((el) => {
			client
				.GET('/api/tag/tag', { fetch, params: { query: { tag_slug: el.dataset.slug } } })
				.then((r) => {
					mount(WorkTag, { target: el, props: { tag: r.data! } });
				})
				.catch(console.log);
		});
	});
</script>

<Section title={data.post.title}>
	<div class="post-content prose prose-neutral prose-sm dark:prose-invert mx-auto max-w-4xl">
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html page}
	</div>
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="post"
		pk={+data.post_id}
	/>
</Section>
