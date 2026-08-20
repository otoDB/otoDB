<script lang="ts">
	import Section from '$lib/Section.svelte';
	import client from '$lib/api';
	import { enumValues, VideoPlatformPrefNames } from '$lib/enums.js';
	import { languages } from '$lib/enums/language.js';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { ThemePref, VideoPlatformPref } from '$lib/schema.js';
	import { themeDisplayOrder, themes } from '$lib/themes/themes.js';
	import { getLocalPrefs, updateLocalPrefs } from '$lib/ui.js';
	import { set_lang } from '$lib/languages.js';

	let { data } = $props();

	let local_prefs = $state(getLocalPrefs());
	let current_theme = $state(data.user?.prefs?.THEME ?? local_prefs?.THEME);
	let video_platform = $state(data.user?.prefs?.VIDEO_PLATFORM ?? local_prefs.VIDEO_PLATFORM);
	let prefer_author_upload = $state(
		data.user?.prefs.PREFER_AUTHOR_UPLOAD ?? local_prefs.PREFER_AUTHOR_UPLOAD
	);

	// "Prefer author uploads" only applies once a specific platform is chosen
	let platform_selected = $derived(video_platform !== VideoPlatformPref.Auto);
	let prefer_author = $derived(platform_selected && prefer_author_upload);

	async function changeTheme(theme: ThemePref) {
		current_theme = theme;
		document.documentElement.setAttribute('data-theme', themes[theme].key);

		if (data.user) await client.POST('/api/user/prefs', { fetch, body: { THEME: theme } });
		else updateLocalPrefs({ THEME: theme });
	}

	async function savePrefs() {
		const body = {
			VIDEO_PLATFORM: video_platform,
			PREFER_AUTHOR_UPLOAD: prefer_author
		};
		if (data.user) await client.POST('/api/user/prefs', { fetch, body });
		else updateLocalPrefs(body);
	}
</script>

<Section title={m.orange_born_seal_ascend()}>
	<div class="flex flex-col gap-8">
		<div>
			<label for="language" class="font-bold">{m.hour_loud_squirrel_ascend()}</label>
			<div class="mt-1 flex items-center gap-2">
				<select
					id="language"
					value={getLocale()}
					onchange={(e) => {
						set_lang(e.currentTarget.value as (typeof locales)[number], !!data.user);
					}}
				>
					{#each locales as l (l)}
						<option value={l}>{languages[l].name}</option>
					{/each}
				</select>
				<span class="text-otodb-content-fainter italic">{m.calm_wide_swan_rest()}</span>
			</div>
		</div>

		<div>
			<div id="theme-label" class="font-bold">{m.acidic_sound_opossum_bump()}</div>
			<div
				class="3xl:grid-cols-5 mt-2 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
				role="radiogroup"
				aria-labelledby="theme-label"
			>
				{#each themeDisplayOrder as theme (theme)}
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
							class="mb-4 h-48 w-full object-cover"
							width={240}
							height={180}
						/>
						{themes[theme].nameFn()}
					</div>
				{/each}
			</div>
		</div>

		<div>
			<label for="video_platform" class="font-bold">{m.merry_bold_finch_soar()}</label>
			<div class="mt-1 flex items-center gap-2">
				<select id="video_platform" bind:value={video_platform} onchange={savePrefs}>
					{#each enumValues(VideoPlatformPref) as platform (platform)}
						<option value={platform}>{VideoPlatformPrefNames[platform]()}</option>
					{/each}
				</select>
				<span class="text-otodb-content-fainter italic">{m.noble_brave_quail_soar()}</span>
			</div>
		</div>

		<div class={[!platform_selected && 'opacity-50']}>
			<label for="prefer_author" class="font-bold">{m.lush_keen_robin_perch()}</label>
			<div class="mt-1 flex items-center gap-2">
				<input
					id="prefer_author"
					type="checkbox"
					disabled={!platform_selected}
					checked={prefer_author}
					onchange={(e) => {
						prefer_author_upload = e.currentTarget.checked;
						savePrefs();
					}}
				/>
				<span class="text-otodb-content-fainter italic">{m.tidy_warm_seal_glide()}</span>
			</div>
		</div>
	</div>
</Section>
