<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, setLocale } from '$lib/paraglide/runtime';

	import { LanguageNames, ThemeNames, Themes } from '$lib/enums';
	import client from '$lib/api';
	import { invalidateAll } from '$app/navigation';
	import { set_lang, update_prefs } from '$lib/ui.js';

	let { data } = $props();

	async function changeBackground(theme) {
		if (data.user) {
			await client.POST('/api/profile/prefs', { fetch, body: { theme, language: null } });
			invalidateAll();
		} else {
			update_prefs({ theme });
			location.reload();
		}
	}
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
		{#each Themes as _, i (i)}
			<button onclick={() => changeBackground(i)} class="py-2 text-lg">
				{ThemeNames[i]()}
			</button>
		{/each}
	</div>
</Section>
