<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import { submission_state } from '$lib/submission_state.svelte';
	import { callErrorToast } from '$lib/toast';

	let { form } = $props();

	const submission = submission_state();

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
	<form use:enhance={submission.enhance} method="POST">
		<table>
			<tbody>
				<tr
					><th><label for="url">URL</label></th><td
						><input type="text" name="url" value={form?.url ?? ''} /></td
					></tr
				>
			</tbody>
		</table>
		<input type="submit" disabled={submission.is_submitting} />
	</form>
</Section>
