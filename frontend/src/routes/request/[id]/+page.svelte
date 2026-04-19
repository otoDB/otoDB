<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import { RequestActions, StatusNames } from '$lib/enums.js';
	import { isSOV, isSVO } from '$lib/enums/language.js';
	import { hasUserLevel } from '$lib/enums/userLevel.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import {
		Levels,
		PathsApiCommentCommentDeleteParametersQueryModel,
		Status
	} from '$lib/schema.js';
	import Section from '$lib/Section.svelte';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTag from '$lib/WorkTag.svelte';
	import type { ComponentProps } from 'svelte';

	let { data } = $props();

	const set = async (status: 0 | 1 | 2) => {
		await client.POST('/api/request/confirm', {
			fetch,
			params: { query: { request_id: data.id, status } }
		});
		invalidateAll();
	};
</script>

{#snippet render_entity(
	ent:
		| ['tagwork', ComponentProps<typeof WorkTag>['tag']]
		| ['mediawork', ComponentProps<typeof WorkCard>['work']]
)}
	{#if ent[0] === 'tagwork'}
		<WorkTag tag={ent[1]} />
	{:else if ent[0] === 'mediawork'}
		<WorkCard work={ent[1]} />
	{/if}
{/snippet}

<Section title={'#' + data.id} type={m.last_jumpy_barbel_mop()}>
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.request.user.username}">{data.request.user.username}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	<h4>
		{StatusNames[data.request.status]()}{#if data.request?.processed_by}(<a
				href="/profile/{data.request.processed_by.username}"
				>{data.request.processed_by.username}</a
			>){/if}
	</h4>

	<ul>
		{#each data.request.requests as r, i (i)}
			<li>
				<code>{RequestActions[r.command as keyof typeof RequestActions]}</code>
				{@render render_entity(r.A as Parameters<typeof render_entity>[0])}
				{@render render_entity(r.B as Parameters<typeof render_entity>[0])}
			</li>
		{/each}
	</ul>
	{#if hasUserLevel(data.user?.level, Levels.Editor) && data.request.status === Status.Pending}
		<button onclick={() => set(1)}>{m.lucky_bold_hornet_push()}</button>
		<button onclick={() => set(2)}>{m.alive_blue_marlin_push()}</button>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model={PathsApiCommentCommentDeleteParametersQueryModel.bulkrequest}
		pk={data.id}
	/>
</Section>
