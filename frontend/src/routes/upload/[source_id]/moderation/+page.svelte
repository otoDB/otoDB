<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ModerationEventsTable from '$lib/ModerationEventsTable.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<Section
	title={data.source?.title || `${m.extra_brave_tapir_skip()} #${data.sourceId}`}
	type={m.minor_inner_lynx_adapt()}
	menuLinks={data.links}
>
	<ModerationEventsTable events={data.events} showTarget={false} />
</Section>
