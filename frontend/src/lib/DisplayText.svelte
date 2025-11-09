<script lang="ts">
	import { getDisplayText } from './api';
	export let value;
	export let placeholder = undefined;
</script>

<span class={value ? "" : "italic"} style:color={value ? "" : "var(--color-otodb-content-fainter)"}>
	{placeholder !== undefined ? getDisplayText(value, placeholder) : getDisplayText(value)}
</span>
