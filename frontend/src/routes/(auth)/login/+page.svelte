<script lang="ts">
	import { goto, invalidateAll } from "$app/navigation";
	import client from "$lib/api.js";
	import Section from "../../Section.svelte";

    let username = $state('');
    let password = $state('');

    let { data } = $props();

    const login = async (e: SubmitEvent) => {
        e.preventDefault();
		const { data: csrf } = await client.GET('/api/auth/csrf');
		if (!csrf)
			return;

		const { data, error } = await client.POST('/api/auth/login', {
			params: { query: { username, password } },
			headers: { 'X-CSRFToken': csrf['csrf_token'] }
		});
		if (error)
			return;
		
		invalidateAll();
		goto('/');
	};
</script>

<svelte:head>
	<title>Login</title>
	<meta name="description" content="Login" />
</svelte:head>

<Section title="Login">
	<form onsubmit={login}>
		<table>
		  <tbody>
			  <tr>
				  <th><label for="username">Username</label></th>
				  <td><input type="text" name="username" bind:value={username}></td>
			  </tr>
			  <tr>
				  <th><label for="password">Password</label></th>
				  <td><input type="password" name="password" bind:value={password}></td>
			  </tr>
		  </tbody>
		  </table>
		<input type="submit" value="Login"/>
	</form>
</Section>
