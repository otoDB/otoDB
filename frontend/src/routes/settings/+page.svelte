<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import Section from '$lib/Section.svelte';
	import client from '$lib/api';
	import { languages } from '$lib/enums/language.js';
	import { themes } from '$lib/themes/themes.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { getLocalTheme, set_lang, updateLocalTheme } from '$lib/ui.js';
	import { ThemePref } from '$lib/schema.js';
	import { enumValues } from '$lib/enums.js';

	let { data } = $props();

	async function changeBackground(theme: ThemePref) {
		if (data.user)
			await client.POST('/api/profile/prefs', { fetch, body: { theme, language: null } });
		else updateLocalTheme(theme);
		invalidateAll();
	}

	let current_locale = $state(getLocale());
	let current_theme = $derived(data.user?.prefs?.theme ?? getLocalTheme() ?? ThemePref.Default);
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
				{languages[key].name}
			</label>
		{/each}
	</div>

	<hr class="my-8" />

	<h2 class="text-lg">{m.acidic_sound_opossum_bump()}</h2>
	<div
		class="3xl:grid-cols-5 mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
		role="radiogroup"
	>
		{#each enumValues(ThemePref) as theme (theme)}
			<label
				class="bg-otodb-bg-faint hover:bg-otodb-bg-fainter has-checked:bg-otodb-bg-fainter cursor-pointer border pb-4 text-center text-lg"
			>
				<img
					src={themes[theme].preview}
					alt={themes[theme].nameFn()}
					class={[
						'mb-4 h-48 w-full object-cover',
						theme === ThemePref.Default && 'invert dark:filter-none'
					]}
					width={240}
					height={180}
				/>
				<input
					class="hidden"
					onclick={() => changeBackground(theme)}
					bind:group={current_theme}
					value={theme}
					type="radio"
				/>{themes[theme].nameFn()}
			</label>
		{/each}
	</div>
</Section>
