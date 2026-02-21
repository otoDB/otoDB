<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import { ProfileConnectionLink, ProfileConnectionTypes, UserLevel } from '$lib/enums';
	import { m } from '$lib/paraglide/messages';
	import Section from '$lib/Section.svelte';
	import { timeAgo } from '$lib/ui';

	let { data } = $props();

	let urls = $state(
		data.connections
			?.map(({ site, content_id }) => ProfileConnectionLink[site](content_id))
			.join('\n') ?? ''
	);

	const invite_interval = 1 * 7 * 24 * 60 * 60 * 1000; // two weeks
	const can_create_invite = $derived(
		data.user.level >= UserLevel.ADMIN ||
			(!data.invites[1] &&
				(data.invites[0].length === 0 ||
					data.invites[0].some(
						(inv) => Date.now() - Date.parse(inv.created_at) >= invite_interval
					)))
	);
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<a href="/reset_password">{m.true_tough_butterfly_sew()}</a>
</Section>
<Section title={m.jumpy_spry_canary_scoop()}>
	<details>
		<summary>{m.fit_noble_niklas_build()}</summary>
		<table>
			<tbody>
				{#each Object.keys(ProfileConnectionTypes).filter((e) => !isNaN(e)) as k, i (i)}
					<tr
						><td>{ProfileConnectionTypes[k]}</td><td
							><code>{ProfileConnectionLink[k]('<code>')}</code></td
						></tr
					>
				{/each}
			</tbody>
		</table>
	</details>
	<form action="?/connections" method="POST" use:enhance>
		<textarea
			bind:value={urls}
			name="urls"
			class="w-full"
			placeholder={m.close_any_racoon_cut()}
		></textarea>
		<input type="submit" />
	</form>
</Section>

{#if data.user.level >= UserLevel.EDITOR}
	<Section title={m.true_male_kudu_cook()}>
		<p>
			{m.sound_flaky_goose_pinch()}
		</p>
		{#if data.invites[0].length}
			<table>
				<tbody>
					<tr
						><th>{m.stale_early_squirrel_prosper()}</th><th
							>{m.tiny_great_robin_commend()}</th
						><th>{m.basic_upper_racoon_type()}</th><th
							>{m.suave_royal_jurgen_shine()}</th
						></tr
					>
					{#each data.invites[0] as inv, i (i)}
						<tr
							><td><time title={new Date(inv.created_at).toLocaleString()}>{timeAgo(inv.created_at)}</time></td><td
								><pre>{inv.secret}</pre></td
							><td>{UserLevel[inv.level]()}</td><td
								>{#if inv.used_by}<a href="/profile/{inv.used_by.username}"
										>{inv.used_by.username}</a
									>{:else}N/A{/if}</td
							></tr
						>
					{/each}
				</tbody>
			</table>
		{/if}
		<form
			inert={!can_create_invite}
			onsubmit={async () => {
				await client.POST('/api/auth/invite', { fetch });
				invalidateAll();
			}}
		>
			{#if !can_create_invite}
				{#if data.invites[1]}
					<p>{m.just_mushy_ladybug_twist({ username: data.invites[1].username })}</p>
				{:else}
					<p>
						{m.next_royal_carp_pride({
							date: new Date(
								Date.parse(data.invites[0][0].created_at) + invite_interval
							).toLocaleString()
						})}
					</p>
				{/if}
			{/if}
			<button type="submit" disabled={!can_create_invite}
				>{m.muddy_that_bobcat_gleam({ level: UserLevel[UserLevel.EDITOR]() })}</button
			>
		</form>
	</Section>
{/if}
