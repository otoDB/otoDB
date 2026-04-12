<script lang="ts">
	import { WorkTagPresentationColours } from './enums';

	type SuggestionTag = {
		id: number;
		name: string;
		slug: string;
		category: number;
		aliased_to?: null | {
			id: number;
			name: string;
			slug: string;
			category: number;
		};
		lang_prefs: { tag: string }[];
		n_instance: number;
	};

	interface Props {
		suggestions: SuggestionTag[];
		onselect: (tag: any) => void;
		onclose?: () => void;
		type: 'work' | 'song';
		query?: string;
	}
	let { suggestions, onselect, onclose, type, query = '' }: Props = $props();

	let selectedIndex = $state(0);

	// Reset selected index when suggestions change
	$effect(() => {
		void suggestions;
		selectedIndex = 0;
	});

	const handleKeyDown = (e: KeyboardEvent) => {
		if (!suggestions.length) return;

		if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = (selectedIndex + 1) % suggestions.length;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = selectedIndex <= 0 ? suggestions.length - 1 : selectedIndex - 1;
		} else if (e.key === 'Enter') {
			e.preventDefault();
			onselect(suggestions[selectedIndex]);
		} else if (e.key === 'Escape') {
			onclose?.();
		}
	};

	const highlightMatch = (text: string, query: string) => {
		if (!query) return { before: text, match: '', after: '' };
		const index = text.toLowerCase().indexOf(query.toLowerCase());
		if (index === -1) return { before: text, match: '', after: '' };
		const result = {
			before: text.slice(0, index),
			match: text.slice(index, index + query.length),
			after: text.slice(index + query.length)
		};
		return result;
	};

	const getTagStyle = (category: number) => {
		return type === 'work' && category !== 0
			? `color: ${WorkTagPresentationColours[category]}`
			: '';
	};
</script>

<svelte:window onkeydown={handleKeyDown} />

{#each suggestions as t, i (i)}
	<li
		class:bg-otodb-bg-fainter={selectedIndex === i}
		class:bg-otodb-bg-faint={selectedIndex !== i}
	>
		<a
			href="/tag/{t.aliased_to?.slug || t.slug}"
			class="flex w-full cursor-pointer justify-between gap-10 px-2 py-1 no-underline"
			onmouseenter={() => (selectedIndex = i)}
			onclick={(e) => {
				if (e.button === 0) {
					e.preventDefault();
					onselect(t);
				}
			}}
		>
			<span class="max-w-60">
				{#if t.aliased_to}
					{@const parts = highlightMatch(t.name, query)}
					{@const aliasedParts = highlightMatch(t.aliased_to.name, query)}
					<span style={getTagStyle(t.aliased_to.category)}>
						{parts.before}<strong>{parts.match}</strong>{parts.after}
					</span>
					<span>→</span>
					<span style={getTagStyle(t.aliased_to.category)}>
						{aliasedParts.before}<strong>{aliasedParts.match}</strong
						>{aliasedParts.after}
					</span>
				{:else}
					{@const parts = highlightMatch(t.name, query)}
					<span style={getTagStyle(t.category)}>
						{parts.before}<strong>{parts.match}</strong>{parts.after}
					</span>
				{/if}
				{#if t.slug !== t.name}
					{@const slugParts = highlightMatch(t.slug, query)}
					<address class="inline">
						({slugParts.before}<strong>{slugParts.match}</strong
						>{slugParts.after}{t.lang_prefs.map((p) => p.tag).join(', ')})
					</address>
				{/if}
			</span>
			<span>{t.n_instance}</span>
		</a>
	</li>
{/each}
