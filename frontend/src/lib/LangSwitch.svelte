<script lang="ts">
	import { locales } from './paraglide/runtime';

	import { LanguageNames } from './enums';
	import { getLocale } from './paraglide/runtime';
	import { onMount } from 'svelte';

	let { value = $bindable(), availableLanguages = locales, className = '' } = $props();
	onMount(() => {
		const i = availableLanguages.find((p) => p === getLocale());
		if (i) value = i;
		else value = availableLanguages[0];
	});
</script>

<div class={className}>
	{#each availableLanguages as l, i (i)}
		<label class="lang-tab">
			<input type="radio" bind:group={value} value={l} />
			{LanguageNames[l]}
		</label>
	{/each}
</div>

<style>
	label.lang-tab {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&:active {
			background-color: var(--otodb-color-bg-faint);
		}
		& > input {
			display: none;
		}
		&:has(> input:checked) {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
		}
	}
</style>
