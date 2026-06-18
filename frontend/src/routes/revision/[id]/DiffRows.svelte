<script lang="ts">
	import type { components } from '$lib/schema';
	import Value from './Value.svelte';

	interface Props {
		change: components['schemas']['RevisionChangeSchema'];
		label: string;
		layout?: 'inline' | 'split';
		windowed?: boolean;
		works: Record<string, components['schemas']['SlimWorkSchema']>;
		labels: Record<string, string>;
	}

	const { change, label, layout = 'inline', windowed = true, works, labels }: Props = $props();

	const segments = $derived(change.diff ?? []);
</script>

<!-- A windowed run of unchanged text: a marker when windowed, the text when not -->
{#snippet gap(text: string)}{#if windowed}<span class="gap">⋯</span>{:else}{text}{/if}{/snippet}

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
		<td class="ind">+</td>
		<td class="font-mono">{label}</td>
		<td><ins>{@render valueOf(change.target_value)}</ins></td>
	</tr>
{:else if layout === 'split'}
	<tr>
		<td class="ind">±</td>
		<td class="font-mono">{label}</td>
		<td class="split">
			<div class="grid grid-cols-2">
				<div class="py-[0.1rem] pr-3 whitespace-pre-wrap">
					{#if change.diff}
						{#each segments as segment, i (i)}{#if segment.op === -1}<del>{segment.text}</del
								>{:else if segment.op === 2}{@render gap(
									segment.text
								)}{:else if segment.op === 0}{segment.text}{/if}{/each}
					{:else}
						<del>{@render valueOf(change.old_value)}</del>
					{/if}
				</div>
				<div class="py-[0.1rem] pl-3 whitespace-pre-wrap">
					{#if change.diff}
						{#each segments as segment, i (i)}{#if segment.op === 1}<ins>{segment.text}</ins
								>{:else if segment.op === 2}{@render gap(
									segment.text
								)}{:else if segment.op === 0}{segment.text}{/if}{/each}
					{:else}
						<ins>{@render valueOf(change.target_value)}</ins>
					{/if}
				</div>
			</div>
		</td>
	</tr>
{:else if change.diff}
	<tr>
		<td class="ind"></td>
		<td class="font-mono">{label}</td>
		<td>
			<span
				>{#each segments as segment, i (i)}{#if segment.op === 1}<ins>{segment.text}</ins
						>{:else if segment.op === -1}<del>{segment.text}</del
						>{:else if segment.op === 2}{@render gap(
							segment.text
						)}{:else}{segment.text}{/if}{/each}</span
			>
		</td>
	</tr>
{:else}
	<tr>
		<td class="ind">−</td>
		<td class="font-mono">{label}</td>
		<td><del>{@render valueOf(change.old_value)}</del></td>
	</tr>
	<tr>
		<td class="ind">+</td>
		<td class="font-mono">{label}</td>
		<td><ins>{@render valueOf(change.target_value)}</ins></td>
	</tr>
{/if}

<style>
	ins,
	del {
		border-radius: var(--radius-xs);
		text-decoration: none;
	}

	/* Large-text diffs (inline segments + split columns) keep coloured text. */
	ins {
		background-color: var(--otodb-color-ins);
	}

	del {
		background-color: var(--otodb-color-del);
	}

	/* Whole-value add/remove rows: plain text, colour the +/- column instead. */
	td > ins,
	td > del {
		background-color: transparent;
	}

	tr {
		&:has(> td > ins) > td.ind {
			border-radius: var(--radius-xs);
			background-color: var(--otodb-color-ins);
		}

		&:has(> td > del) > td.ind {
			border-radius: var(--radius-xs);
			background-color: var(--otodb-color-del);
		}
	}

	td > span {
		white-space: pre-wrap;
	}

	/* Collapsed unchanged region between context windows. */
	.gap {
		display: block;
		text-align: center;
		color: var(--otodb-color-content-faint);
		user-select: none;
	}

	td.split {
		position: relative;
		padding-block: 0;
	}

	td.split::after {
		content: '';
		position: absolute;
		inset-block: -1px;
		left: 50%;
		border-left: 1px solid var(--otodb-color-content-faint);
	}
</style>
