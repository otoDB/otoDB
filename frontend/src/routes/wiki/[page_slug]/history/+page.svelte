<script lang="ts">
	import HistoryView from '$lib/HistoryView.svelte';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();
</script>

<Section title={data.head.title} type={m.curly_zesty_pelican_aim()} menuLinks={data.menuLinks}>
	<HistoryView revisions={data.history} batch_size={data.batch_size} />
</Section>
