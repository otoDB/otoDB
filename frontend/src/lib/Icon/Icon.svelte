<script module lang="ts">
	import { m } from '$lib/paraglide/messages';

	// Keys must name what the icon means (e.g. 'external-link'), not the icon's shape or name (e.g. 'globe').
	export const icons = {
		'thread-closed': {
			icon: 'icon-[gravity-ui--check]',
			label: m.topical_small_alligator_aspire()
		},
		'thread-opened': {
			icon: 'icon-[gravity-ui--comment]',
			label: m.flat_tasty_okapi_cut()
		},
		'language': {
			icon: 'icon-[gravity-ui--globe]',
			label: m.hour_loud_squirrel_ascend()
		},
		'notifications': {
			icon: 'icon-[gravity-ui--bell]',
			label: m.free_keen_wren_exhale()
		},
		'notifications-unread': {
			icon: 'icon-[gravity-ui--bell-fill]',
			label: m.free_keen_wren_exhale()
		}
	} as const satisfies Record<string, { icon: string; label: string }>;
</script>

<script lang="ts">
	import type { ClassValue } from 'svelte/elements';

	interface Props {
		class?: ClassValue;
		key: keyof typeof icons;
		/**
		 * Set when an ancestor element already exposes an accessible name for this icon
		 * (e.g. adjacent visible text or an aria-label on a parent link/button).
		 * Otherwise the icon's own aria-label would duplicate that name for screen readers.
		 */
		decorative?: boolean;
	}

	const { key, decorative = false, ...props }: Props = $props();
</script>

{#if decorative}
	<span class={[icons[key].icon, props.class]} aria-hidden="true"></span>
{:else}
	<span
		class={[icons[key].icon, props.class]}
		role="img"
		aria-label={icons[key].label}
		title={icons[key].label}
	></span>
{/if}
