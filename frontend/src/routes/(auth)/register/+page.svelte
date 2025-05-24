<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { form }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
</script>

<svelte:head>
	<title>{m.blue_whole_camel_type()}</title>
</svelte:head>

<Section title={m.blue_whole_camel_type()}>
	<form method="POST" use:enhance>
		{#if form?.missing}<p class="error">{m.tiny_round_shark_express()}</p>{/if}
		{#if form?.failed}<p class="error">{form.message}</p>{/if}
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
					<th><label for="invite">{m.tiny_great_robin_commend()}</label></th>
					<td><input required type="text" name="invite" /></td>
				</tr>
				<tr>
					<th><label for="username">{m.moving_funny_spider_feast()}</label></th>
					<td><input required type="text" name="email" value={form?.email ?? ''} /></td>
				</tr>
				<tr>
					<th><label for="password">{m.vexed_merry_niklas_greet()}</label></th>
					<td><input required type="password" name="password" /></td>
				</tr>
				<tr>
					<th><label for="username">{m.lofty_pretty_maggot_hope()}</label></th>
					<td><input required type="password" name="confirm" /></td>
				</tr>
			</tbody>
		</table>
		<input type="submit" value={m.blue_whole_camel_type()} />
	</form>
</Section>
