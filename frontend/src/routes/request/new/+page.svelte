<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import { submission_state } from '$lib/submission_state.svelte';

	let { data } = $props();
	import { m } from '$lib/paraglide/messages.js';

	const submission = submission_state();
</script>

<Section title={m.muddy_tough_swan_view()}>
	<a href="/post/5">{m.grassy_warm_gadfly_inspire()}</a>
	<form method="POST" use:enhance={submission.enhance}>
		<textarea rows="10" class="w-full" name="actions" required>{data.preFilledData ?? ''}</textarea>
		<input type="submit" disabled={submission.is_submitting} />
	</form>
</Section>
