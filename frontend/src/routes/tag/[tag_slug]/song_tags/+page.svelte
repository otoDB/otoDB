<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api';
	import Section from '$lib/Section.svelte';
	import TagsField from '$lib/TagsField.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();

	let tags: string[] = $state(data.tag.song!.tags.map((t) => t.slug));
	const submit_tags = async () => {
		await client.POST('/api/tag/song_tags', {
			fetch,
			params: { query: { song_id: +data.tag.song!.id } },
			body: tags
		});
		goto(`/tag/${data.tag.slug}`, { invalidateAll: true });
	};
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.grand_nice_pony_belong(),
		name: data.tag.song!.title
	})}
	menuLinks={data.song_links}
>
	<TagsField type="song" class="w-full" bind:value={tags} />
	<input type="submit" onclick={submit_tags} />
</Section>
