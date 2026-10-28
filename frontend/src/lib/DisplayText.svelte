<script lang="ts">
	import { getDisplayText } from './ui';

	interface Props {
		value: string | null | undefined;
		placeholder?: string;
	}

	const { value, placeholder }: Props = $props();
</script>

<span class={value == null ? 'text-otodb-content-fainter italic' : undefined}>
	{getDisplayText(value, placeholder)}
</span>
