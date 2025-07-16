<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>{m.plane_inner_chipmunk_race()}</title>
</svelte:head>

<Section
	title={m.plane_inner_chipmunk_race()}
	menuLinks={[
		{ pathname: 'list/new', title: m.swift_dry_gecko_boost() },
		{ pathname: 'list/import', title: m.kind_tiny_lemur_praise() }
	]}
>
	<form use:enhance method="POST">
		{#if form?.failed}<p class="error">{m.green_due_javelina_pop()}</p>{/if}
		<table>
			<tbody>
				<tr
					><th><label for="name">{m.large_factual_octopus_exhale()}</label></th><td
						><input type="text" name="name" value={form?.name ?? ''} /></td
					></tr
				>
				<tr
					><th><label for="description">{m.clear_lucky_peacock_pick()}</label></th><td
						><textarea name="description" value={form?.description ?? ''}
						></textarea></td
					></tr
				>
			</tbody>
		</table>
		<input type="submit" />
	</form>
</Section>
