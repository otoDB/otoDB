<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';

	let { data, form } = $props();
	import { m } from '$lib/paraglide/messages.js';
	import { callErrorToast } from '$lib/toast';

	$effect(() => {
		if (form?.missing) {
			callErrorToast(m.tiny_round_shark_express());
		}
		if (form?.mismatch) {
			callErrorToast(m.front_clean_termite_treat());
		}
	});
</script>

<Section title={m.true_tough_butterfly_sew()}>
	{#if form?.reset_success}
		<p>{m.stock_jolly_crocodile_cheer()}</p>
	{:else if data.token || data.user}
		<form method="POST" use:enhance action="?/reset">
			<table>
				<tbody>
					<tr>
						<th><label for="password">{m.factual_lazy_puma_delight()}</label></th>
						<td><input required type="password" name="password" /></td>
					</tr>
					<tr>
						<th><label for="confirm">{m.lofty_pretty_maggot_hope()}</label></th>
						<td><input required type="password" name="confirm" /></td>
					</tr>
				</tbody>
			</table>
			<input hidden type="text" name="token" value={data.token} />
			<input type="submit" />
		</form>
	{:else if form?.success}
		<p>{m.grand_lucky_halibut_chop()}</p>
	{:else}
		<form method="POST" use:enhance action="?/request">
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
