<script>
	import client from '$lib/api.js';
	import { ProfileConnectionTypes } from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import { debounce } from '$lib/ui.js';

	let { data } = $props();

	const update_connection = async (e) => {
		const el = e.target;
		if (el.value.trim() === '')
			await client.DELETE('/api/profile/connection', {
				fetch,
				params: { query: { site: +el.name, username: data.user.username } }
			});
		else
			await client.PUT('/api/profile/connection', {
				body: { content_id: el.value.trim(), site: +el.name },
				params: { query: { username: data.user.username } }
			});
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
<Section title="Connections">
	<table>
		<thead>
			<tr>
				<td>Site</td>
				<td>ID</td>
			</tr>
		</thead><tbody>
			{#each Object.keys(ProfileConnectionTypes)
				.filter((e) => !isNaN(e))
				.toSorted() as s, i (i)}
				<tr>
					<td>{ProfileConnectionTypes[s]}</td>
					<td
						><input
							type="text"
							name={s}
							value={data.connections?.find(({ site }) => site === +s)?.content_id ??
								''}
							oninput={debounce(update_connection)}
						/></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</Section>
