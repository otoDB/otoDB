<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { form }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<svelte:head>
	<title>{m.clean_cuddly_sparrow_learn()}</title>
</svelte:head>

<Section title={m.clean_cuddly_sparrow_learn()}>
	<form method="POST" use:enhance>
		<textarea class="w-full" name="actions"> </textarea>
		<input type="submit" />
	</form>
</Section>
