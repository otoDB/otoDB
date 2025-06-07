<script lang="ts">
	import { goto } from '$app/navigation';
	import client from '$lib/api.js';
	import {
		ProfileConnectionLink,
		ProfileConnectionParsers,
		ProfileConnectionTypes
	} from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';

	let { data } = $props();

	let urls = $state(
		data.connections
			?.map(({ site, content_id }) => ProfileConnectionLink[site](content_id))
			.join('\n') ?? ''
	);

	const update_connections = async (e: SubmitEvent) => {
		e.preventDefault();
		const connections = [...new Set(urls.split('\n'))]
			.filter((x) => x.trim() !== '')
			.map((url) =>
				ProfileConnectionParsers.map((p, i) => ({ site: i, content_id: p(url) }))
					.filter((v) => !!v.content_id)
					.at(-1)
			)
			.filter((v) => !!v);
		await client.PUT('/api/profile/connection', {
			body: connections,
			params: { query: { username: data.user.username } }
		});
		goto(`/profile/${data.user.username}`, { invalidateAll: true });
	};
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	...
</Section>
<Section title={m.jumpy_spry_canary_scoop()}>
	<details>
		<summary>{m.fit_noble_niklas_build()}</summary>
		<table>
			<tbody>
				{#each Object.keys(ProfileConnectionTypes).filter((e) => !isNaN(e)) as k}
					<tr
						><td>{ProfileConnectionTypes[k]}</td><td
							><code>{ProfileConnectionLink[k]('<code>')}</code></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</details>
	<form onsubmit={update_connections}>
		<textarea bind:value={urls} class="w-full"> </textarea>
		<input type="submit" />
	</form>
</Section>
