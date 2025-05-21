<script lang="ts">
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	import { m } from '$lib/paraglide/messages.js';
	import { UserLevel } from '$lib/enums';
	import CommentTree from '$lib/CommentTree.svelte';

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
		{m.sharp_witty_jackdaw_treat({date: new Date(data.profile.date_created).toLocaleDateString() })}
	</p>
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="account"
		pk={data.profile.id}
	/>
</Section>
