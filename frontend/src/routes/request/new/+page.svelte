<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';

	let { data } = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<Section title={m.muddy_tough_swan_view()}>
	<a href="/post/5">{m.grassy_warm_gadfly_inspire()}</a>
	<form method="POST" use:enhance>
		<textarea rows="10" class="w-full" name="actions" required
			>{data.preFilledData ?? ''}</textarea
		>
		<input type="submit" />
	</form>
</Section>
