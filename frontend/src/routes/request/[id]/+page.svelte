<script lang="ts">
	import { RequestActions, Status } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime.js';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/ui.js';
	import WorkCard from '$lib/WorkCard.svelte';
	import WorkTag from '$lib/WorkTag.svelte';

	let { data } = $props();
</script>

{#snippet render_entity(ent)}
	{#if ent[0] === 'tagwork'}
		<WorkTag tag={ent[1]} />
	{:else if ent[0] === 'mediawork'}
		<WorkCard work={ent[1]} />
	{/if}
{/snippet}

<Section title={m.mild_loud_shad_enchant({ type: m.last_jumpy_barbel_mop(), name: '#' + data.id })}>
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.user.username}">{data.user.username}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	<h4>{Status[data.status]()}</h4>

	<ul>
		{#each data.requests as r, i (i)}
			<li>
				<code>{RequestActions[r.command]}</code>
				{@render render_entity(r.A)}
				{@render render_entity(r.B)}
			</li>
		{/each}
	</ul>
</Section>
