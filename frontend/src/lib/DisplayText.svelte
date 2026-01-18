<script lang="ts">
	import { getDisplayText } from './api';
	export let value;
	export let placeholder = undefined;
</script>

<span class={value ?? 'text-otodb-content-fainter italic'}>
	{getDisplayText(value, placeholder)}
</span>
