<script lang="ts">
	import { enhance } from '$app/forms';
	import { ProfileConnectionLink, ProfileConnectionTypes } from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	let urls = $state(
		data.connections
			?.map(({ site, content_id }) => ProfileConnectionLink[site](content_id))
			.join('\n') ?? ''
	);
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	<a href="/reset_password">{m.true_tough_butterfly_sew()}</a>
</Section>
<Section title={m.jumpy_spry_canary_scoop()}>
	<details>
		<summary>{m.fit_noble_niklas_build()}</summary>
		<table>
			<tbody>
				{#each Object.keys(ProfileConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
					<tr
						><td>{ProfileConnectionTypes[k]}</td><td
							><code>{ProfileConnectionLink[k]('<code>')}</code></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</details>
	<form action="?/connections" method="POST" use:enhance>
		<textarea bind:value={urls} name="urls" class="w-full"> </textarea>
		<input type="submit" />
	</form>
</Section>
