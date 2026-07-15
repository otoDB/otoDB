<script lang="ts">
	import type { ClassValue } from 'svelte/elements';
	import icons from './icons';

	interface Props {
		class?: ClassValue;
		key: keyof typeof icons;
	}

	const { key, ...props }: Props = $props();
</script>

<span
	class={['inline-block', icons[key].icon, props.class]}
	role="img"
	aria-label={icons[key].label}
	title={icons[key].label}
></span>
