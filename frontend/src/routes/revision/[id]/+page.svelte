<script lang="ts">
	import { m } from '$lib/paraglide/messages';
	import { getLocale } from '$lib/paraglide/runtime';
	import Section from '$lib/Section.svelte';
	import { isSOV, isSVO } from '$lib/ui';

	let { data } = $props();
</script>

<Section title="{m.arable_direct_swan_glow()} #{data.revision.id}">
	<h3>
		{#if isSVO(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
		<a href="/profile/{data.revision.user}">{data.revision.user}</a>
		{#if isSOV(getLocale())}
			{m.curly_safe_lynx_fond()}
		{/if}
	</h3>
	{#if data.revision.message}<h4>{data.revision.message}</h4>{/if}

	<pre>{#each data.revision.changes as c, i (i)}{c.target_type} #{c.target_id} - {#if c.deleted}Deleted{:else}{c.target_column} -> {c.target_value}{/if}
		{/each}</pre>
</Section>
