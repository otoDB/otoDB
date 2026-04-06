<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { getVersionKey, Version } from '$lib/ui';
	import { resolveUserLevelById, UserLevel } from '$lib/enums/UserLevel';
	import { ProfileConnection, resolveProfileConnectionNameById } from '$lib/enums/ProfileConnection';

	let { data }: PageProps = $props();

	const profileLd =
		'<script type="application/ld+json">' +
		JSON.stringify({
			'@context': 'https://schema.org',
			'@type': 'ProfilePage',
			dateCreated: data.profile.date_created,
			mainEntity: {
				'@type': 'Person',
				name: data.profile.username,
				url: `https://otodb.net/profile/${data.profile.username}`
			}
		}) +
		'</' +
		'script>';
</script>

<svelte:head>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html profileLd}
</svelte:head>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<p>{UserLevel[resolveUserLevelById(data.profile.level)].nameFn()}</p>
	{#if data.profile.date_created}
		<p>
			{m.sharp_witty_jackdaw_treat({
				date: new Date(data.profile.date_created).toLocaleDateString()
			})}{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
				content: Version[getVersionKey(new Date(data.profile.date_created))].name
			})}
		</p>
	{/if}

	{#if data.connections}
		<ul class="list-none">
			{#each data.connections as s, i (i)}
				<li>
					<ConnectionFavicon
						type={ProfileConnection[resolveProfileConnectionNameById(s.site)].name}
						class="inline size-4"
					/>
					<a
						href={ProfileConnection[resolveProfileConnectionNameById(s.site)].linkFn(
							s.content_id
						)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{decodeURI(
							ProfileConnection[resolveProfileConnectionNameById(s.site)].linkFn(
								s.content_id
							)
						)}
					</a>
				</li>
			{/each}
		</ul>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="account"
		pk={data.profile.id}
	/>
</Section>
