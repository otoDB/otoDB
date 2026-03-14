<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ModerationEventsTable from '$lib/ModerationEventsTable.svelte';
	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<Section title={data.title} type={m.grand_merry_fly_succeed()} menuLinks={data.links}>
	<ModerationEventsTable events={data.events} isEditor={data.isEditor} showTarget={false} />
</Section>
