<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from '$lib/enums';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Rejected sources</title>
</svelte:head>

<Section title="Rejected sources" menuLinks={data.links}>
	<ul>
		{#each data.sources as src}
			<li>
				<span>
					<h3>
						<a href={src.url} target="_blank" rel="noopener noreferrer">{src.title}</a>
					</h3>
					<h4>
						Requested by: <a href="/profile/{src.added_by.username}"
							>{src.added_by.username}</a
						>
					</h4>
					<h4>{Platform[src.platform]} {src.published_date}</h4>
					<h4>Claimed origin: {WorkOrigin[src.work_origin]()}</h4>
					<h4>Rejected reason: {src.rejection_reason}</h4>
				</span>
				<span>
					<a href={src.url} target="_blank" rel="noopener noreferrer"
						><img
							src={src.thumbnail}
							alt={src.title}
							class="float-right clear-both w-50"
						/></a
					>
				</span>
			</li>
		{:else}
			<li>There are no rejected sources.</li>
		{/each}
	</ul>
</Section>

<style>
	ul > li {
		display: flex;
		background-color: var(--otodb-fainter-bg);
		justify-content: space-between;
		margin: 1rem 0;
		padding: 1rem;
	}
</style>
