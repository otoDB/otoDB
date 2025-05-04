<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>{m.proof_heroic_rat_cuddle()}</title>
</svelte:head>

<Section
	title={m.proof_heroic_rat_cuddle()}
	menuLinks={[
		{ pathname: 'list/new', title: m.swift_dry_gecko_boost() },
		{ pathname: 'list/import', title: m.kind_tiny_lemur_praise() }
	]}
>
	<p>{m.mild_loud_shad_enchant({ type: m.nimble_drab_gorilla_cut(), name: '' })}</p>
	<ul>
		<li>YouTube Playlists</li>
		<li>Niconico Mylists</li>
		<li>Bilibili Playlists</li>
	</ul>
	<form use:enhance method="POST">
		{#if form?.failed}<p class="error">Failed!</p>{/if}
		<table>
			<tbody>
				<tr
					><th><label for="url">URL</label></th><td
						><input type="text" name="url" value={form?.url ?? ''} /></td
					></tr
				>
			</tbody>
		</table>
		<input type="submit" />
	</form>
</Section>
