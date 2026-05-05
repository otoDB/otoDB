<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import Connections from '$lib/Connections.svelte';
	import { getVersionKey, versions } from '$lib/enums/version';
	import { userLevelNames } from '$lib/enums/userLevel.js';
	import { profileConnectionMap } from '$lib/enums/profileConnection.js';
	import { ModelsWithComments } from '$lib/schema.js';
	import Time from '$lib/Time.svelte';
	import { ParaglideMessage } from '@inlang/paraglide-js-svelte';

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
	<p>
		<ParaglideMessage message={m.sharp_witty_jackdaw_treat} inputs={{}}>
			{#snippet date()}
				<Time format="absolute" date={data.profile.date_created} />
			{/snippet}
		</ParaglideMessage>{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
			content: versions[getVersionKey(new Date(data.profile.date_created))].name
		})}
	</p>

	{#if data.connections}
		<Connections items={data.connections} map={profileConnectionMap} />
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
