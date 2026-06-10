<script lang="ts">
	import type { components } from '$lib/schema';
	import Value from './Value.svelte';

	interface Props {
		change: components['schemas']['RevisionChangeSchema'];
		card?: boolean;
		works: Map<string, components['schemas']['SlimWorkSchema']>;
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
		{card}
		{works}
		{labels}
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

	ins {
		background-color: var(--otodb-color-ins);
	}

	del {
		background-color: var(--otodb-color-del);
	}

	div:has(> ins) > span {
		color: var(--otodb-color-ins);
	}

	div:has(> del) > span {
		color: var(--otodb-color-del);
	}
</style>
