<script lang="ts">
	import { getDisplayText } from './api';
	export let value;
	export let placeholder = undefined;
</script>

<span class={value !== null && value !== undefined ? "" : "italic"} style:color={value !== null && value !== undefined ? "" : "var(--color-otodb-content-fainter)"}>
	{placeholder !== undefined ? getDisplayText(value, placeholder) : getDisplayText(value)}
</span>
