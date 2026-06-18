<script lang="ts">
	import RefValue from './RefValue.svelte';
	import { displayValue } from './displayValue';

	interface Props {
		targetType: string;
		column: string;
		value: string | null | undefined;
		ref?: string | null;
		card?: boolean;
	}
	const { targetType, column, value, ref, card = false }: Props = $props();
</script>

{#if ref}
	<RefValue {ref} id={value} {card} />
{:else}
	<span class="whitespace-pre-wrap">{displayValue(targetType, column, value)}</span>
{/if}
