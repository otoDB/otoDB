<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';

	import { LanguageNames, ThemeNames, Themes } from '$lib/enums';
	import client from '$lib/api';
	import { get_prefs, set_lang, update_prefs } from '$lib/ui.js';

	let { data } = $props();

	async function changeBackground(theme) {
		if (data.user) {
			await client.POST('/api/profile/prefs', { fetch, body: { theme, language: null } });
		} else {
			update_prefs({ theme });
		}
		location.reload();
	}

	let current_locale = $state(getLocale());
	let current_theme = $state(data.user?.prefs?.theme ?? +get_prefs()?.theme);
</script>

<Section title={m.orange_born_seal_ascend()}>
	<h2 class="text-lg">{m.hour_loud_squirrel_ascend()}</h2>
	<div class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-4">
		{#each locales as key (key)}
			<label
				class="bg-otodb-bg-faint has-checked:bg-otodb-bg-fainter hover:bg-otodb-bg-fainter mb-2 cursor-pointer border px-4 py-4 text-center text-lg"
			>
				<input
					class="hidden"
					type="radio"
					bind:group={current_locale}
					value={key}
					onchange={() => {
						set_lang(current_locale, !!data.user);
					}}
				/>
				{LanguageNames[key]}
			</label>
		{/each}
	</div>

	<hr class="my-8" />

	<h2 class="text-lg">{m.acidic_sound_opossum_bump()}</h2>
	<div
		class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5"
	>
		{#each Themes as _, i (i)}
			<label
				class="bg-otodb-bg-faint has-checked:bg-otodb-bg-fainter hover:bg-otodb-bg-fainter mb-2 cursor-pointer border px-4 py-4 text-center text-lg"
			>
				<input
					class="hidden"
					type="radio"
					bind:group={current_theme}
					value={i}
					onchange={() => changeBackground(i)}
				/>
				{ThemeNames[i]()}
			</label>
		{/each}
	</div>
</Section>
