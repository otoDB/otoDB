<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import client from "$lib/api.js";

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
	};
	const logout = async () => {
		await client.POST('/api/auth/logout');

		invalidateAll();
	};
</script>

<svelte:head>
	<title>Login</title>
	<meta name="description" content="Login" />
</svelte:head>

<div class="text-column">
	<h1>Login</h1>
	{#if data.user}
	You are already logged in, {data.user.name}!
	<button onclick={logout}>Logout</button>
	{:else}
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
	{/if}
</div>
