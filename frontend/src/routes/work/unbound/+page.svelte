<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from '$lib/enums';
	import UnboundSourceActions from './UnboundSourceActions.svelte';
	import RefreshButton from '../RefreshButton.svelte';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>{m.suave_gray_stork_type()}</title>
</svelte:head>

<Section title={m.suave_gray_stork_type()} menuLinks={data.links}>
	<ul>
		{#each data.sources as src, i (i)}
			<li>
				<span>
					<h3>
						<a href={src.url} target="_blank" rel="noopener noreferrer">{src.title}</a>
					</h3>
					<h4>
						{m.swift_sweet_anaconda_hurl()}
						<a href="/profile/{src.added_by.username}">{src.added_by.username}</a>
					</h4>
					<h4>{Platform[src.platform]} {src.published_date}</h4>
					<h4>
						{m.mild_loud_shad_enchant({
							type: m.large_polite_otter_thrive(),
							name: WorkOrigin[src.work_origin]()
						})}
					</h4>
					<RefreshButton source={src} />
					<UnboundSourceActions source={src} />
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
			<li>{m.moving_such_seal_hug()}</li>
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
