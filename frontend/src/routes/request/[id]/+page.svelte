<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import client from '$lib/api.js';
	import CommentTree from '$lib/CommentTree.svelte';
	import { RequestActions, Status, UserLevel } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/ui.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTag from '$lib/WorkTag.svelte';

	let { data } = $props();

	const set = async (status: number) => {
		await client.POST('/api/request/confirm', {
			fetch,
			params: { query: { request_id: data.id, status } }
		});
		invalidateAll();
	};
</script>

{#snippet render_entity(ent)}
	{#if ent[0] === 'tagwork'}
		<WorkTag tag={ent[1]} />
	{:else if ent[0] === 'mediawork'}
		<WorkCard work={ent[1]} />
	{/if}
{/snippet}

<svelte:head>
	<title
		>{m.mild_loud_shad_enchant({ type: m.last_jumpy_barbel_mop(), name: '#' + data.id })}</title
	>
</svelte:head>

<Section title={'#' + data.id}
	type={m.last_jumpy_barbel_mop()}> 
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
		{Status[data.request.status]()}{#if data.request?.processed_by}(<a
				href="/profile/{data.request.processed_by.username}"
				>{data.request.processed_by.username}</a
			>){/if}
	</h4>

	<ul>
		{#each data.request.requests as r, i (i)}
			<li>
				<code>{RequestActions[r.command]}</code>
				{@render render_entity(r.A)}
				{@render render_entity(r.B)}
			</li>
		{/each}
	</ul>
	{#if data.user.level >= UserLevel.EDITOR && data.request.status === 0}
		<button onclick={() => set(1)}>{m.lucky_bold_hornet_push()}</button>
		<button onclick={() => set(2)}>{m.alive_blue_marlin_push()}</button>
	{/if}
</Section>

<Section title={m.same_broad_haddock_pinch()}>
	<CommentTree
		comments={data.comments}
		user={data.user ?? null}
		model="bulkrequest"
		pk={data.id}
	/>
</Section>
