<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();
</script>

<Section title={data.head.title} type={m.giant_away_scallop_hike()} menuLinks={data.menuLinks}>
	<HistoryView revisions={data.history.items} user={data.user} />
</Section>
