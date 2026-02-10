<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import { callErrorToast } from '$lib/toast';

	let { form }: PageProps = $props();

	$effect(() => {
		if (form?.failed) {
			callErrorToast(m.green_due_javelina_pop());
		}
	});
</script>

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
		<li>SoundCloud Playlists</li>
	</ul>
	<form use:enhance method="POST">
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
