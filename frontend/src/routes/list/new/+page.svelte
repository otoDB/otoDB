<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { hasUserLevel } from '$lib/enums/userLevel';
	import { Levels } from '$lib/schema';

	import { m } from '$lib/paraglide/messages.js';
	import { enhance } from '$app/forms';
	import { callErrorToast } from '$lib/toast';

	let { data, form } = $props();

	$effect(() => {
		if (form?.failed) {
			callErrorToast(m.green_due_javelina_pop());
		}
	});
</script>

<Section
	title={m.plane_inner_chipmunk_race()}
	menuLinks={[
		{ pathname: 'list/new', title: m.swift_dry_gecko_boost() },
		...(hasUserLevel(data.user?.level, Levels.Editor)
			? [{ pathname: 'list/import', title: m.kind_tiny_lemur_praise() }]
			: [])
	]}
>
	<form use:enhance method="POST">
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
