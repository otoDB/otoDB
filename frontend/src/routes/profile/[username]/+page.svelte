<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { ProfileConnectionTypes, ProfileConnectionLink, UserLevel } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';
	import { x } from '@inlang/paraglide-js/urlpattern-polyfill';

	let { data }: PageProps = $props();
</script>

<Section
	title={m.mild_loud_shad_enchant({
		type: m.fuzzy_crazy_cobra_lead(),
		name: data.profile.username
	})}
	menuLinks={data.links}
>
	<p>{UserLevel[data.profile?.level]()}</p>
	<p>
		{m.sharp_witty_jackdaw_treat({
			date: new Date(data.profile.date_created).toLocaleDateString()
		})}
	</p>

	{#if data.connections}
		<ul class="list-none">
			{#each data.connections as s, i (i)}
				<li>
					<img
						src="/connection_favicons/{ProfileConnectionTypes[s.site]}.png"
						alt={ProfileConnectionTypes[s.site]}
						class="inline size-4"
					/>
					<a
						href={ProfileConnectionLink[s.site](s.content_id)}
						target="_blank"
						rel="noopener noreferrer"
					>
						{ProfileConnectionTypes[s.site]}
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
