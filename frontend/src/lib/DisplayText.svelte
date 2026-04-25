<script lang="ts">
	import { getDisplayText } from './ui';

	interface Props {
		value: string | null | undefined;
		placeholder?: string;
	}

	const { value, placeholder }: Props = $props();
</script>

<span class={value ?? 'text-otodb-content-fainter italic'}>
	{getDisplayText(value, placeholder)}
</span>
