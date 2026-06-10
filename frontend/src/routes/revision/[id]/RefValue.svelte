<script lang="ts">
	import WorkCard from '$lib/WorkCard.svelte';
	import { buildEntityRoutes, isValidEntityModelType } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages';
	import type { components } from '$lib/schema';

	interface Props {
		ref: string;
		id: string | null | undefined;
		/** Render mediawork refs as a work card instead of a title link */
		card?: boolean;
		works: Map<string, components['schemas']['SlimWorkSchema']>;
		labels: Record<string, string>;
	}
	const { ref, id, card = false, works, labels }: Props = $props();

	const work = $derived(ref === 'mediawork' && id != null ? works.get(id) : undefined);
	const label = $derived(
		id != null ? (labels[`${ref}:${id}`] ?? work?.title ?? undefined) : undefined
	);
	const href = $derived.by(() => {
		if (id == null || !isValidEntityModelType(ref)) return undefined;
		// Tag and profile routes are slug/username-based; that's the label
		if (ref === 'tagwork' || ref === 'tagsong' || ref === 'account')
			return label ? buildEntityRoutes(ref, label) : undefined;
		return buildEntityRoutes(ref, id);
	});
</script>

{#if id == null}
	<span>{m.pale_blunt_moth_lack()}</span>
{:else if card && work}
	<div class="grid w-44 grid-rows-[auto_auto]">
		<WorkCard {work} />
	</div>
{:else if href}
	<a {href}>{label ?? `#${id}`}</a>
{:else}
	<span>{label ?? `#${id}`}</span>
{/if}
