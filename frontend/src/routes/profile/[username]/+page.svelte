<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { ProfileConnectionTypes, ProfileConnectionLink, UserLevel } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import { version_end_dates } from '$lib/ui';

	let { data }: PageProps = $props();

	const profileJsonLd = JSON.stringify({
		'@context': 'https://schema.org',
		'@type': 'ProfilePage',
		dateCreated: data.profile.date_created,
		mainEntity: {
			'@type': 'Person',
			name: data.profile.username,
			url: `https://otodb.net/profile/${data.profile.username}`
		}
	});
</script>

<svelte:head>
	{@html `<script type="application/ld+json">${profileJsonLd}</script>`}
</svelte:head>

<Section title={data.profile.username} type={m.fuzzy_crazy_cobra_lead()} menuLinks={data.links}>
	<p>{UserLevel[data.profile?.level]()}</p>
	<p>
		{m.sharp_witty_jackdaw_treat({
			date: new Date(data.profile.date_created).toLocaleDateString()
		})}{m.great_clean_beaver_amuse()}{m.awful_house_liger_expand({
			content: version_end_dates.find(
				(d) => d[1] - Date.parse(data.profile.date_created) >= 0
			)?.[0]
		})}
	</p>

	{#if data.connections}
		<ul class="list-none">
			{#each data.connections as s, i (i)}
				<li>
					<ConnectionFavicon
						type={ProfileConnectionTypes[s.site]}
						class="inline size-4"
					/>
					<a
						href={ProfileConnectionLink[s.site](s.content_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{decodeURI(ProfileConnectionLink[s.site](s.content_id))}
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
