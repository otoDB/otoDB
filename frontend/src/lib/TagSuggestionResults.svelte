<script lang="ts">
	let { suggestions, onclick, type } = $props();
	$effect(() => {
		console.log(suggestions);
	});
</script>

{#each suggestions as t, i (i)}
	<li
		class="bg-otodb-bg-fainter hover:bg-otodb-bg-faint flex w-full justify-between gap-10 px-2 py-1"
	>
		<a class="max-w-60 cursor-pointer" href={null} onclick={(...rest) => onclick(t, ...rest)}
			>{t.aliased_to ? `${t.name} → ${t.aliased_to.name}` : t.name}
			{#if t.slug !== t.name}<address class="inline">
					({t.slug}<!-- TODO extend lang prefs to song tags -->{#if type === 'work'}{[
							'',
							...t.lang_prefs
						]
							.map((p) => p.tag)
							.join(', ')}{/if})
				</address>{/if}</a
		>
		<span>{t.n_instance}</span>
	</li>
{/each}
