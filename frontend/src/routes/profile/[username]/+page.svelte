<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { getVersionKey, versions } from '$lib/enums/version';
	import { userLevelNames } from '$lib/enums/userLevel.js';
	import { profileConnectionMap } from '$lib/enums/profileConnection.js';
	import { ModelsWithComments } from '$lib/schema.js';

	let { data } = $props();

	const profileLd = $derived(
		'<script type="application/ld+json">' +
			JSON.stringify({
				'@context': 'https://schema.org',
				'@type': 'ProfilePage',
				'dateCreated': data.profile.date_created,
				'mainEntity': {
					'@type': 'Person',
					'name': data.profile.username,
					'url': `https://otodb.net/profile/${data.profile.username}`
				}
			}) +
			'</' +
			'script>'
	);
</script>

<svelte:head>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html profileLd}
</svelte:head>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<p>{userLevelNames[data.profile.level]()}</p>
	{#if data.profile.date_created}
		<p>
			{m.sharp_witty_jackdaw_treat({
				date: new Date(data.profile.date_created).toLocaleDateString()
			})}{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
				content: versions[getVersionKey(new Date(data.profile.date_created))].name
			})}
		</p>
	{/if}

	{#if data.connections}
		<ul class="list-none">
			{#each data.connections as s, i (i)}
				<li>
					<ConnectionFavicon
						type={profileConnectionMap[s.site].name}
						class="inline size-4"
					/>
					<a
						href={profileConnectionMap[s.site].linkFn(s.content_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{decodeURI(profileConnectionMap[s.site].linkFn(s.content_id))}
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
		model={ModelsWithComments.account}
		pk={data.profile.id}
	/>
</Section>
