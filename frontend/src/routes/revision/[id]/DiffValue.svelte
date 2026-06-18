<script lang="ts">
	import type { components } from '$lib/schema';
	import Value from './Value.svelte';

	interface Props {
		change: components['schemas']['RevisionChangeSchema'];
		card?: boolean;
		works: Record<string, components['schemas']['SlimWorkSchema']>;
		labels: Record<string, string>;
	}

	const { change, card = false, works, labels }: Props = $props();
</script>

{#snippet valueOf(value: string | null | undefined)}
	<Value
		targetType={change.target_type}
		column={change.target_column ?? ''}
		{value}
		ref={change.ref}
		{works}
		{labels}
		{card}
	/>
{/snippet}

{#if change.created}
	<ins>{@render valueOf(change.target_value)}</ins>
{:else}
	<div class="flex flex-col items-start gap-1">
		<div class="flex items-center gap-1">
			<span>−</span>
			<del>{@render valueOf(change.old_value)}</del>
		</div>
		<div class="flex items-center gap-1">
			<span>+</span>
			<ins>{@render valueOf(change.target_value)}</ins>
		</div>
	</div>
{/if}

<style>
	ins,
	del {
		border-radius: var(--radius-xs);
		text-decoration: none;
	}

	/* Standalone "created" value keeps its background as the only add cue. */
	ins {
		background-color: var(--otodb-color-ins);
	}

	del {
		background-color: var(--otodb-color-del);
	}

	/* In the −/+ change view, colour the indicator and leave the value plain. */
	div:has(> span) > ins,
	div:has(> span) > del {
		background-color: transparent;
	}

	div:has(> ins) > span {
		border-radius: var(--radius-xs);
		padding-inline: 0.25rem;
		background-color: var(--otodb-color-ins);
	}

	div:has(> del) > span {
		border-radius: var(--radius-xs);
		padding-inline: 0.25rem;
		background-color: var(--otodb-color-del);
	}
</style>
