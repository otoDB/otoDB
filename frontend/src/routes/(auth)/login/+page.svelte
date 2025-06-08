<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { form }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<svelte:head>
	<title>{m.inner_stale_anteater_walk()}</title>
</svelte:head>

<Section title={m.inner_stale_anteater_walk()}>
	<form method="POST" use:enhance>
		{#if form?.missing}<p class="error">{m.tiny_round_shark_express()}</p>{/if}
		{#if form?.failed}<p class="error">{m.careful_lost_jaguar_dart()}</p>{/if}
		<table>
			<tbody>
				<tr>
					<th><label for="username">{m.careful_cozy_elk_dare()}</label></th>
					<td
						><input
							required
							type="text"
							name="username"
							value={form?.username ?? ''}
						/></td
					>
				</tr>
				<tr>
					<th><label for="password">{m.vexed_merry_niklas_greet()}</label></th>
					<td><input required type="password" name="password" /></td>
				</tr>
			</tbody>
		</table>
		<address>
			<a href="/reset_password">{m.zippy_tense_raven_favor()}</a>
		</address>
		<input type="submit" value={m.inner_stale_anteater_walk()} />
	</form>
</Section>
