<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from '$lib/enums';
	import WorkThumbnail from '$lib/WorkThumbnail.svelte';

	let { data }: PageProps = $props();
</script>

<Section title={m.weird_lucky_hornet_grip()} menuLinks={data.links}>
	<ul>
		{#each data.sources as src, i (i)}
			<li>
				<span>
					<h3>
						<a href={src.url} target="_blank" rel="noopener noreferrer"
							>{src.title || src.url}</a
						>
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
					<h4>
						{m.mild_loud_shad_enchant({
							type: m.weary_spicy_fly_attend(),
							name: src.rejection.reason
						})}
					</h4>
				</span>
				<span>
					<a href={src.url} target="_blank" rel="noopener noreferrer"
						><WorkThumbnail
							thumbnail={src.thumbnail}
							alt={src.title || src.url}
							class="float-right clear-both aspect-video w-50"
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
		background-color: var(--otodb-color-bg-fainter);
		justify-content: space-between;
		margin: 1rem 0;
		padding: 1rem;
	}
</style>
