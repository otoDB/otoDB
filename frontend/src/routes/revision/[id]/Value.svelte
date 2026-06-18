<script lang="ts">
	import WorkCard from '$lib/WorkCard.svelte';
	import { buildEntityRoutes, isValidEntityModelType } from '$lib/enums.js';
	import { m } from '$lib/paraglide/messages';
	import { displayValue } from './displayValue';
	import { getRevisionRefs } from './refs';

	interface Props {
		targetType: string;
		column: string;
		value: string | null | undefined;
		ref?: string | null;
		/** Render mediawork refs as a work card instead of a title link */
		card?: boolean;
	}
	const { targetType, column, value, ref, card = false }: Props = $props();

	const refs = getRevisionRefs();
	const work = $derived(ref === 'mediawork' && value != null ? refs.works[value] : undefined);
	const label = $derived(
		value != null ? (refs.labels[`${ref}:${value}`] ?? work?.title ?? undefined) : undefined
	);
	const href = $derived.by(() => {
		if (value == null || !ref || !isValidEntityModelType(ref)) return undefined;
		// Tag and profile routes are slug/username-based; that's the label
		if (ref === 'tagwork' || ref === 'tagsong' || ref === 'account')
			return label ? buildEntityRoutes(ref, label) : undefined;
		return buildEntityRoutes(ref, value);
	});
</script>

{#if ref && isValidEntityModelType(ref)}
	{#if value == null}
		<span>{m.pale_blunt_moth_lack()}</span>
	{:else if card && work}
		<div class="grid w-44 grid-rows-[auto_auto]">
			<WorkCard {work} />
		</div>
	{:else if href}
		<a {href}>{label ?? `#${value}`}</a>
	{:else}
		<span>{label ?? `#${value}`}</span>
	{/if}
{:else}
	<span class="whitespace-pre-wrap">{displayValue(targetType, column, value)}</span>
{/if}
