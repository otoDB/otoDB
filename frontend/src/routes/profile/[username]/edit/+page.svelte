<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import { m } from '$lib/paraglide/messages';
	import {
		allProfileConnectionKeys,
		ProfileConnection,
		resolveProfileConnectionNameById
	} from '$lib/ProfileConnection.js';
	import Section from '$lib/Section.svelte';
	import { timeAgo } from '$lib/ui';
	import { resolveUserLevelById, UserLevel } from '$lib/UserLevel.js';

	let { data } = $props();

	let urls = $state(
		data.connections
			?.map(({ site, content_id }) =>
				ProfileConnection[resolveProfileConnectionNameById(site)].linkFn(content_id)
			)
			.join('\n') ?? ''
	);

	const invite_interval = 1 * 7 * 24 * 60 * 60 * 1000; // two weeks
	const deniedInviteCreationReason:
		| { reason: 'no invites data' }
		| { reason: 'restricted invitee exists'; username: string }
		| { reason: 'expired invite exists'; next: number }
		| null = $derived.by(() => {
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
				reason: 'expired invite exists',
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
				{#each allProfileConnectionKeys as k (k)}
					<tr
						><td>{ProfileConnection[k].name}</td><td
							><code>{ProfileConnection[k].linkFn('<code>')}</code></td
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

{#if data.user.level >= UserLevel.EDITOR.id}
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
								<time title={new Date(inv.created_at).toLocaleString()}>
									{timeAgo(inv.created_at)}
								</time>
							</td>
							<td><pre>{inv.secret}</pre></td>
							<td>{UserLevel[resolveUserLevelById(inv.level)].nameFn()}</td>
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
			{:else if deniedInviteCreationReason?.reason === 'expired invite exists'}
				<p>
					{m.next_royal_carp_pride({
						date: new Date(deniedInviteCreationReason.next).toLocaleString()
					})}
				</p>
			{/if}

			<button type="submit" disabled={!!deniedInviteCreationReason}>
				{m.muddy_that_bobcat_gleam({ level: UserLevel.EDITOR.nameFn() })}
			</button>
		</form>
	</Section>
{/if}
