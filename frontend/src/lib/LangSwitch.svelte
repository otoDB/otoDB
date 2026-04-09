<script lang="ts">
	import { languages } from './enums/Languages';

	let {
		availableLanguages,
		value = $bindable()
	}: {
		value: keyof typeof languages;
		availableLanguages: (keyof typeof languages)[];
	} = $props();
</script>

<div class="float-right">
	{#each availableLanguages as l (l)}
		<label class="lang-tab">
			<input type="radio" bind:group={value} value={l} />
			{languages[value].name}
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
