<script lang="ts">
	import type { components } from '$lib/schema';
	import { diffWords } from 'diff';
	import Value from './Value.svelte';
	import { hasDisplayHandler } from './displayValue';

	interface Props {
		change: components['schemas']['RevisionChangeSchema'];
		label: string;
		works: Map<string, components['schemas']['SlimWorkSchema']>;
		labels: Record<string, string>;
	}

	const { change, label, works, labels }: Props = $props();

	// Word-level diffs only make sense for free text, not enums or references
	const useWordDiff = $derived(
		!change.ref &&
			!hasDisplayHandler(change.target_type, change.target_column) &&
			typeof change.old_value === 'string' &&
			typeof change.target_value === 'string' &&
			change.old_value.length > 255
	);

	const segments = $derived(
		useWordDiff ? diffWords(change.old_value ?? '', change.target_value ?? '') : []
	);
</script>

{#snippet valueOf(value: string | null | undefined)}
	<Value
		targetType={change.target_type}
		column={change.target_column ?? ''}
		{value}
		ref={change.ref}
		{works}
		{labels}
	/>
{/snippet}

{#if change.created}
	<tr>
		<td>+</td>
		<td>{label}</td>
		<td><ins>{@render valueOf(change.target_value)}</ins></td>
	</tr>
{:else if useWordDiff}
	<tr>
		<td></td>
		<td>{label}</td>
		<td>
			<span
				>{#each segments as segment, i (i)}{#if segment.added}<ins>{segment.value}</ins
						>{:else if segment.removed}<del>{segment.value}</del
						>{:else}{segment.value}{/if}{/each}</span
			>
		</td>
	</tr>
{:else}
	<tr>
		<td>−</td>
		<td>{label}</td>
		<td><del>{@render valueOf(change.old_value)}</del></td>
	</tr>
	<tr>
		<td>+</td>
		<td>{label}</td>
		<td><ins>{@render valueOf(change.target_value)}</ins></td>
	</tr>
{/if}

<style>
	ins,
	del {
		border-radius: var(--radius-xs);
	}

	ins {
		text-decoration: none;
		background-color: var(--otodb-color-ins);
	}

	del {
		text-decoration: none;
		background-color: var(--otodb-color-del);
	}

	tr {
		&:has(> td > ins) > td:first-child {
			color: var(--otodb-color-ins);
		}

		&:has(> td > del) > td:first-child {
			color: var(--otodb-color-del);
		}
	}

	td > span {
		white-space: pre-wrap;
	}
</style>
