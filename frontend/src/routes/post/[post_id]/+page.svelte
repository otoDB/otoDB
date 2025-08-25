<script lang="ts">
	import CommentTree from '$lib/CommentTree.svelte';
	import LangSwitch from '$lib/LangSwitch.svelte';
	import Section from '$lib/Section.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import client from '$lib/api.js';
	import { LanguageNames, Languages } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import { mount, unmount } from 'svelte';

	let { data } = $props();
	let lang_view = $derived(
		data.post.pages.some((p) => p.lang === Languages[getLocale()])
			? getLocale()
			: Languages[data.post.pages[0].lang]
	);
	let page_object = $derived(data.post.pages.find((p) => p.lang === Languages[lang_view]));
	let page = $derived(
		page_object.page_rendered.replaceAll(
			/&lt;otodb-worktag\s*slug="(.+?)"\s*\/&gt;/g,
			'<otodb-worktag data-slug="$1"></otodb-worktag>'
		)
	);
	$effect(() => {
		if (page) {
			const tags = Array.from(document.querySelectorAll('.post-content otodb-worktag')).map(
				(el) =>
					client
						.GET('/api/tag/tag', {
							fetch,
							params: { query: { tag_slug: el.dataset.slug } }
						})
						.then((r) => mount(WorkTag, { target: el, props: { tag: r.data! } }))
			);
			return () => {
				tags.forEach((p) => p.then(unmount));
			};
		}
	});
</script>

<Section title={data.post.title}>
	<LangSwitch
		availableLanguages={data.post.pages.map((v) => Languages[v.lang])}
		bind:value={lang_view}
	/>
	{m.mild_loud_shad_enchant({
		type: m.lower_full_opossum_bless(),
		name: new Date(page_object.modified).toLocaleString()
	})}
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
