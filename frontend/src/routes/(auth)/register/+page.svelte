<script lang="ts">
	import { enhance } from "$app/forms";
	import Section from "../../Section.svelte";
	import type { PageProps } from "./$types";
	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>Register</title>
</svelte:head>

<Section title="Register">
	<form method="POST" use:enhance>
		{#if form?.missing}<p class="error">All fields are required.</p>{/if}
        {#if form?.failed}<p class="error">Authentication failed!</p>{/if}
		<table>
		<tbody>
			<tr>
				<th><label for="username">Username</label></th>
				<td><input type="text" name="username" value={form?.username ?? ''}></td>
			</tr>
			<tr>
				<th><label for="username">Email</label></th>
				<td><input type="text" name="email" value={form?.email ?? ''}></td>
			</tr>
			<tr>
				<th><label for="password">Password</label></th>
				<td><input type="password" name="password"></td>
			</tr>
			<tr>
				<th><label for="username">Confirm Password</label></th>
				<td><input type="password" name="confirm"></td>
			</tr>
		</tbody>
		</table>
		<input type="submit" value="Login"/>
	</form>
</Section>
