<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({
			type: m.fuzzy_crazy_cobra_lead(),
			name: data.profile.username
		})}</title
	>
</svelte:head>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	{#if data.user?.username === data.profile.username}
		<a href="/list/new">Make a new list...</a>
		<a href="/list/import">Import list...</a>
	{/if}
	<ul class="list-disc">
		{#each data.lists as list (list)}
			<li><a href="/list/{list.id}">{list.name}</a></li>
		{:else}
			<li>This user has no lists!</li>
		{/each}
	</ul>
</Section>
