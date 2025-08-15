<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from '../$types';

	let { data }: PageProps = $props();
</script>

<Section
	title={m.mild_loud_shad_enchant({ type: m.giant_away_scallop_hike(), name: data.tag.name })}
	menuLinks={data.links}
>
	<HistoryView historicals={data.history.items} />
</Section>
