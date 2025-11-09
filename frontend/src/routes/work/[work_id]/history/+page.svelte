<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from '../$types';

	let { data }: PageProps = $props();
</script>

<Section titleType={m.giant_away_scallop_hike()} titleName={data.title} menuLinks={data.links}>
	<HistoryView historicals={data.history.items} user={data.user} />
</Section>
