<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { form, data }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<svelte:head>
	<title>{m.clean_cuddly_sparrow_learn()}</title>
</svelte:head>

<Section title={m.clean_cuddly_sparrow_learn()}>
	<a href="/post/5">{m.grassy_warm_gadfly_inspire()}</a>
	<form method="POST" use:enhance>
		<textarea rows="10" class="w-full" name="actions" required
			>{data.preFilledData ?? ''}</textarea
		>
		<input type="submit" />
	</form>
</Section>
