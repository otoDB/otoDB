<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { data, form }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<svelte:head>
	<title>{m.true_tough_butterfly_sew()}</title>
</svelte:head>

<Section title={m.true_tough_butterfly_sew()}>
	{#if data.token || data.user}
		<form method="POST" use:enhance action="?/reset">
			<input hidden type="text" name="token" value={data.token} />
			{#if form?.missing}<p class="error">{m.tiny_round_shark_express()}</p>{/if}
			{#if form?.unmatch}<p class="error">{m.front_clean_termite_treat()}</p>{/if}
			<table>
				<tbody>
					<tr>
						<th><label for="password">New password</label></th>
						<td><input required type="password" name="password" /></td>
					</tr>
					<tr>
						<th><label for="confirm">{m.lofty_pretty_maggot_hope()}</label></th>
						<td><input required type="password" name="confirm" /></td>
					</tr>
				</tbody>
			</table>
			<input type="submit" />
		</form>
	{:else if form?.success}
		<p>{m.grand_lucky_halibut_chop()}</p>
	{:else}
		<form method="POST" use:enhance action="?/request">
			{#if form?.missing}<p class="error">{m.tiny_round_shark_express()}</p>{/if}
			<table>
				<tbody>
					<tr>
						<th><label for="email">Email:</label></th>
						<td><input type="email" name="email" required /></td>
					</tr>
				</tbody>
			</table>
			<input type="submit" />
		</form>
	{/if}
</Section>
