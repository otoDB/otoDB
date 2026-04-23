<script lang="ts">
	import Section from '$lib/Section.svelte';
	import client from '$lib/api';
	import { enumValues } from '$lib/enums.js';
	import { languages } from '$lib/enums/language.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { ThemePref } from '$lib/schema.js';
	import { themes } from '$lib/themes/themes.js';
	import { getLocalPref, set_lang, updateLocalPref } from '$lib/ui.js';

	let { data } = $props();

	let current_locale = $state(getLocale());
	let current_theme = $state(data.user?.prefs?.THEME ?? getLocalPref('THEME'));

	async function changeTheme(theme: ThemePref) {
		current_theme = theme;
		document.documentElement.setAttribute('data-theme', themes[theme].key);

		if (data.user) await client.POST('/api/profile/prefs', { fetch, body: { THEME: theme } });
		else updateLocalPref('THEME', theme);
	}
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
			<div
				class="bg-otodb-bg-faint hover:bg-otodb-bg-fainter aria-checked:bg-otodb-bg-fainter cursor-pointer border pb-4 text-center text-lg"
				role="radio"
				aria-checked={current_theme === theme}
				tabindex="0"
				onclick={() => changeTheme(theme)}
				onkeydown={(e) => {
					if (e.key === 'Enter' || e.key === ' ') changeTheme(theme);
				}}
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
				{themes[theme].nameFn()}
			</div>
		{/each}
	</div>
</Section>
