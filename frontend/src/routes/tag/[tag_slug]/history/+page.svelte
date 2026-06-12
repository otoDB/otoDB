<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();
</script>

<Section title={data.tag.name} type={m.giant_away_scallop_hike()} menuLinks={data.links}>
	<HistoryView revisions={data.history} batch_size={data.batch_size} />
</Section>

{#if data.tag.song && data.song_history}
	<Section
		title={data.tag.song.title}
		type={m.giant_away_scallop_hike()}
		menuLinks={data.song_links}
	>
		<HistoryView
			revisions={data.song_history}
			batch_size={data.batch_size}
			page_param="song_page"
		/>
	</Section>
{/if}
