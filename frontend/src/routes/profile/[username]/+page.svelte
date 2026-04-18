<script lang="ts">
	import Section from '$lib/Section.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { getVersionKey, Version } from '$lib/enums/version';
	import { PathsApiCommentCommentDeleteParametersQueryModel } from '$lib/schema.js';
	import { UserLevelNames } from '$lib/enums/UserLevel.js';
	import { ProfileConnectionMap } from '$lib/enums/ProfileConnection.js';

	let { data } = $props();

	const profileLd =
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
		'script>';
</script>

<svelte:head>
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html profileLd}
</svelte:head>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<p>{UserLevelNames[data.profile.level]()}</p>
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
						type={ProfileConnectionMap[s.site].name}
						class="inline size-4"
					/>
					<a
						href={ProfileConnectionMap[s.site].linkFn(s.content_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{decodeURI(ProfileConnectionMap[s.site].linkFn(s.content_id))}
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
		model={PathsApiCommentCommentDeleteParametersQueryModel.account}
		pk={data.profile.id}
	/>
</Section>
