<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { Platform, WorkOrigin } from '$lib/enums';
	import UnboundSourceActions from './UnboundSourceActions.svelte';
	import RefreshButton from '../RefreshButton.svelte';
	import { invalidate, invalidateAll } from '$app/navigation';

	let { data }: PageProps = $props();

	let actions = Array(data.sources.length).fill(undefined);
	const submit = async () => {
		await Promise.all(actions.map(a => a.submit()));
		invalidateAll();
	}
</script>

<svelte:head>
	<title>{m.suave_gray_stork_type()}</title>
</svelte:head>

<Section title={m.suave_gray_stork_type()} menuLinks={data.links}>
	<input type="submit" onclick={submit}/>
	{#if data.sources.length}
	<table class="w-full">
		<thead><tr>
			<th>{m.knotty_due_hamster_wave()}</th>
			<th>{m.heroic_ideal_orangutan_aid()}</th>
			<th>No Action</th>
			<th>{m.lucky_bold_hornet_push()}</th>
			<th>{m.alive_blue_marlin_push()}</th>
		</tr></thead>
		<tbody>
		{#each data.sources as src, i (i)}
			<tr>
				<td>
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
				</td>
				<td>
					<a href={src.url} target="_blank" rel="noopener noreferrer"
						><img
							src={src.thumbnail}
							alt={src.title}
							class="float-right clear-both w-50"
						/></a
					>
				</td>
				<UnboundSourceActions source={src} bind:this={actions[i]} />
			</tr>
		{/each}
	</tbody></table>
	{:else}
	<h3>{m.moving_such_seal_hug()}</h3>
	{/if}
</Section>
