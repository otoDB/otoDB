<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import { enumValues } from '$lib/enums.js';
	import { profileConnectionMap } from '$lib/enums/profileConnection.js';
	import { hasUserLevel, userLevelNames } from '$lib/enums/userLevel.js';
	import { m } from '$lib/paraglide/messages';
	import { Levels, ProfileConnectionTypes } from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import Time from '$lib/Time.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

	let { data } = $props();

	let urls = $state(
		data.connections
			?.map(({ site, content_id }) => profileConnectionMap[site].linkFn(content_id))
			.join('\n') ?? ''
	);

	const invite_interval = 1 * 7 * 24 * 60 * 60 * 1000; // two weeks
	const deniedInviteCreationReason:
		| { reason: 'no invites data' }
		| { reason: 'restricted invitee exists'; username: string }
		| { reason: 'next invite not yet available'; next: number }
		| null = $derived.by(() => {
		if (hasUserLevel(data.user?.level, Levels.Admin)) return null;
		if (!data.invites) return { reason: 'no invites data' };
		if (data.invites.restrictedInvitee)
			return {
				reason: 'restricted invitee exists',
				username: data.invites.restrictedInvitee.username
			};
		if (
			data.invites.invites.some(
				(inv) => Date.now() - Date.parse(inv.created_at) < invite_interval
			)
		)
			return {
				reason: 'next invite not yet available',
				next: Date.parse(data.invites.invites[0].created_at) + invite_interval
			};

		return null;
	});
</script>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<a href="/reset_password">{m.true_tough_butterfly_sew()}</a>
</Section>
<Section title={m.jumpy_spry_canary_scoop()}>
	<details>
		<summary>{m.fit_noble_niklas_build()}</summary>
		<table>
			<tbody>
				{#each enumValues(ProfileConnectionTypes) as k (k)}
					<tr
						><td>{profileConnectionMap[k].name}</td><td
							><code>{profileConnectionMap[k].linkFn('<code>')}</code></td
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

{#if hasUserLevel(data.user?.level, Levels.Editor)}
	<Section title={m.true_male_kudu_cook()}>
		<p>
			{m.sound_flaky_goose_pinch()}
		</p>
		{#if data.invites && data.invites?.invites.length > 0}
			<table>
				<tbody>
					<tr
						><th>{m.stale_early_squirrel_prosper()}</th><th
							>{m.tiny_great_robin_commend()}</th
						><th>{m.basic_upper_racoon_type()}</th><th
							>{m.suave_royal_jurgen_shine()}</th
						></tr
					>
					{#each data.invites.invites as inv, i (i)}
						<tr>
							<td>
								<Time format="relative" date={inv.created_at} />
							</td>
							<td><pre>{inv.secret}</pre></td>
							<td>{userLevelNames[inv.level]()}</td>
							<td>
								{#if inv.used_by}
									<a href="/profile/{inv.used_by.username}">
										{inv.used_by.username}
									</a>
								{:else}
									N/A
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
		<form
			inert={!!deniedInviteCreationReason}
			onsubmit={async () => {
				await client.POST('/api/auth/invite', { fetch });
				invalidateAll();
			}}
		>
			{#if deniedInviteCreationReason?.reason === 'restricted invitee exists'}
				<p>
					{m.just_mushy_ladybug_twist({
						username: deniedInviteCreationReason.username
					})}
				</p>
			{:else if deniedInviteCreationReason?.reason === 'next invite not yet available'}
				<p>
					<ParaglideMessage message={m.next_royal_carp_pride} inputs={{}}>
						{#snippet date()}
							<Time
								format="absolute"
								date={new Date(deniedInviteCreationReason.next)}
							/>
						{/snippet}
					</ParaglideMessage>
				</p>
			{/if}

			<button type="submit" disabled={!!deniedInviteCreationReason}>
				{m.muddy_that_bobcat_gleam({ level: userLevelNames[Levels.Editor]() })}
			</button>
		</form>
	</Section>
{/if}
