<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';

	let { data } = $props();
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	{#if data.user?.username === data.profile.username}
		<a href="/list/new">{m.plane_inner_chipmunk_race()}</a>
		<a href="/list/import">{m.proof_heroic_rat_cuddle()}</a>
	{/if}
	<ul class="list-disc">
		{#each data.lists as list, i (i)}
			<li><a href="/list/{list.id}">#{list.id} - {list.name}</a></li>
		{:else}
			<li>{m.quiet_stout_haddock_persist()}</li>
		{/each}
	</ul>
</Section>
