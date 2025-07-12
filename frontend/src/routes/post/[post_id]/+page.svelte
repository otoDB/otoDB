<script lang="ts">
	import CommentTree from '$lib/CommentTree.svelte';
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<svelte:head>
	<title>{data.post.title}</title>
</svelte:head>

<Section title={data.post.title}>
	<div class="post-content prose prose-neutral prose-sm dark:prose-invert mx-auto max-w-4xl">
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html data.post.post_rendered}
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
