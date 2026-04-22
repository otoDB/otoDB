<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ModerationEventsTable from '$lib/ModerationEventsTable.svelte';

	let { data } = $props();
</script>

<Section
	title={data.source?.title || `Source #${data.sourceId}`}
	type="Moderation"
	menuLinks={data.links}
>
	<ModerationEventsTable events={data.events} showTarget={false} />
</Section>
