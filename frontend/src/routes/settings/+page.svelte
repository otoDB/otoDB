<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale } from '$lib/paraglide/runtime';

	import { LanguageNames } from '$lib/enums';
	import { set_lang, theme, type Theme } from '$lib/ui.js';
	import client from '$lib/api.js';
	let { data } = $props();

	const changeTheme = async (nt: Theme) => {
		theme.set(nt);
		if (data.user) {
			await client.POST('/api/profile/prefs', {
				fetch,
				body: {
					theme: {
						auto: 0,
						'light-simple': 1,
						'dark-simple': 2,
						'dark-aniki': 3
					}[nt],
					language: null
				}
			});
		}
	};
</script>

<Section title={m.orange_born_seal_ascend()}>
	<h2 class="text-lg">{m.hour_loud_squirrel_ascend()}</h2>
	<div class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-4">
		{#each ['en', 'ja', 'ko', 'zh-cn'] as const as key (key)}
			<button
				aria-pressed={getLocale() === key}
				onclick={() => set_lang(key, !!data.user)}
				class="bg-otodb-bg-faint aria-pressed:bg-otodb-bg-fainter hover:bg-otodb-bg-fainter mb-2 cursor-pointer px-4 py-4 text-lg"
			>
				{LanguageNames[key]}
			</button>
		{/each}
	</div>

	<hr class="my-8" />

	<h2 class="text-lg">{m.acidic_sound_opossum_bump()}</h2>
	<div
		class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5"
	>
		<button
			onclick={() => changeTheme('auto')}
			class={['py-2 text-lg', { 'bg-otodb-bg-fainter': $theme === 'auto' }]}
		>
			{m.misty_muddy_sparrow_work()}
		</button>
		<button
			onclick={() => changeTheme('light-simple')}
			class={['py-2 text-lg', { 'bg-otodb-bg-fainter': $theme === 'light-simple' }]}
		>
			{m.vexed_away_spider_skip()}
		</button>
		<button
			onclick={() => changeTheme('dark-simple')}
			class={['py-2 text-lg', { 'bg-otodb-bg-fainter': $theme === 'dark-simple' }]}
		>
			{m.late_that_eagle_care()}
		</button>
		<button
			onclick={() => changeTheme('dark-aniki')}
			class={['py-2 text-lg', { 'bg-otodb-bg-fainter': $theme === 'dark-aniki' }]}
		>
			{m.next_ago_opossum_swim()}
		</button>
	</div>
</Section>
