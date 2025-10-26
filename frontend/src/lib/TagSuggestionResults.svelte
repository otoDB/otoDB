<script lang="ts">
	import { WorkTagPresentationColours } from './enums';
	import { makeTagDisplayName } from './api';

	let { suggestions, selectedIndex, onclick, onhover, type, query = '' } = $props();

	const highlightMatch = (text: string, query: string) => {
		const displayText = makeTagDisplayName(text);
		if (!query) return { before: displayText, match: '', after: '' };
		const index = text.toLowerCase().indexOf(query.toLowerCase());
		if (index === -1) return { before: displayText, match: '', after: '' };
		const result = {
			before: displayText.slice(0, index),
			match: displayText.slice(index, index + query.length),
			after: displayText.slice(index + query.length)
		};
		return result;
	};

	const getTagStyle = (category: number) => {
		return type === 'work' && category !== 0
			? `color: ${WorkTagPresentationColours[category]}`
			: '';
	};
</script>

{#each suggestions as t, i (i)}
	<li
		class:bg-otodb-bg-fainter={selectedIndex === i}
		class:bg-otodb-bg-faint={selectedIndex !== i}
	>
		<a
			href="/tag/{t.aliased_to?.slug || t.slug}"
			class="flex w-full cursor-pointer justify-between gap-10 px-2 py-1 no-underline"
			onmouseenter={() => onhover(i)}
			onclick={(e) => {
				if (e.button === 0) {
					e.preventDefault();
					onclick(t, e);
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
						>{slugParts.after}<!-- TODO extend lang prefs to song tags -->{#if type === 'work'}{[
								'',
								...t.lang_prefs
							]
								.map((p) => p.tag)
								.join(', ')}{/if})
					</address>
				{/if}
			</span>
			<span>{t.n_instance}</span>
		</a>
	</li>
{/each}
