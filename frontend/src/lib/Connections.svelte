<script lang="ts" generics="S extends number">
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';

	type Item = { site: S; content_id: string; dead?: boolean | null };

	let {
		items,
		map
	}: {
		items: Item[];
		map: Record<S, { name: string; linkFn: (id: string) => string }>;
	} = $props();

	const sorted = $derived(
		items.toSorted((a, b) => {
			const aWebsite = map[a.site].name === 'Website';
			const bWebsite = map[b.site].name === 'Website';
			// Sort by dead status, generic website URL, site name, content_id
			return (
				Number(!!a.dead) - Number(!!b.dead) ||
				Number(aWebsite) - Number(bWebsite) ||
				map[a.site].name.localeCompare(map[b.site].name) ||
				a.content_id.localeCompare(b.content_id)
			);
		})
	);
</script>

{#each sorted as s (`${s.site}:${s.content_id}`)}
	<li class={{ 'opacity-60': s.dead }}>
		<ConnectionFavicon type={map[s.site].name} class="inline size-4" />
		<a
			href={map[s.site].linkFn(s.content_id)}
			target="_blank"
			rel="noopener noreferrer"
			class={{ 'line-through': s.dead }}
		>
			{map[s.site].linkFn(s.content_id)}
		</a>
	</li>
{/each}
