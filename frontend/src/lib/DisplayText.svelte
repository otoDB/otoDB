<script lang="ts">
	import { getDisplayText } from './api';
	export let value;
	export let placeholder = undefined;
</script>

<span
	class={value ?? 'italic text-otodb-content-fainter'}
>
	{getDisplayText(value, placeholder)}
</span>
