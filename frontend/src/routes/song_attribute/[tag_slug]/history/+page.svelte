<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();
</script>

<Section title={data.tag.name} type={m.giant_away_scallop_hike()} menuLinks={data.links}>
	<HistoryView revisions={data.history.items} user={data.user} />
</Section>
