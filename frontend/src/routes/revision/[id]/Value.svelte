<script lang="ts">
	import type { components } from '$lib/schema';
	import RefValue from './RefValue.svelte';
	import { displayValue } from './displayValue';

	interface Props {
		targetType: string;
		column: string;
		value: string | null | undefined;
		ref?: string | null;
		card?: boolean;
		works: Map<string, components['schemas']['SlimWorkSchema']>;
		labels: Record<string, string>;
	}
	const { targetType, column, value, ref, card = false, works, labels }: Props = $props();
</script>

{#if ref}
	<RefValue {ref} id={value} {card} {works} {labels} />
{:else}
	<span class="whitespace-pre-wrap">{displayValue(targetType, column, value)}</span>
{/if}
