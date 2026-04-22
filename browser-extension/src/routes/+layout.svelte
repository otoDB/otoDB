<script lang="ts">
	import { onMount } from "svelte";
	import { languages } from "$lib/enums/language";
	import {
		defineCustomClientStrategy,
		setLocale,
	} from "$lib/paraglide/runtime";
	import { ThemePref } from "$lib/schema";
	import { themes } from "$lib/themes/themes";
	import "../styles.css";

	const CACHE = "otodb.theme";

	let resolvedLang: keyof typeof languages | undefined = $state(undefined);
	let themeClass = $state(
		localStorage.getItem(CACHE) ?? themes[ThemePref.Default].cssKey,
	);

	defineCustomClientStrategy("custom-userPreference", {
		getLocale: () => resolvedLang,
		setLocale: () => {},
	});

	let { children } = $props();

	async function pickDefaultLocale(): Promise<
		keyof typeof languages | undefined
	> {
		const accept = await chrome.i18n.getAcceptLanguages();
		for (const l of accept) {
			const key = l.toLowerCase();
			if (key in languages) return key as keyof typeof languages;
			const base = key.split("-")[0];
			if (base in languages) return base as keyof typeof languages;
		}
	}

	function langKeyById(id: number | null | undefined) {
		if (id == null) return undefined;
		for (const [k, v] of Object.entries(languages))
			if (v.id === id) return k as keyof typeof languages;
	}

	onMount(async () => {
		const [fallbackLocale, { prefs }] = await Promise.all([
			pickDefaultLocale(),
			chrome.storage.local.get("prefs") as Promise<{
				prefs?: { LANGUAGE?: number; THEME?: ThemePref };
			}>,
		]);

		resolvedLang = langKeyById(prefs?.LANGUAGE) ?? fallbackLocale;
		if (resolvedLang) setLocale(resolvedLang, { reload: false });

		themeClass = themes[prefs?.THEME ?? ThemePref.Default].cssKey;
		localStorage.setItem(CACHE, themeClass);

		// Frontend components link with relative paths like `/tag/foo` which
		// would otherwise resolve to chrome-extension://.../tag/foo.
		// Intercept every click on anchors and open in a browser tab on otodb.net,
		// preserving modifier/middle-click "open in background tab" semantics.
		function handleLinkClick(e: MouseEvent) {
			if (e.defaultPrevented) return;
			const a = (e.target as HTMLElement | null)?.closest("a");
			if (!a) return;
			const href = a.getAttribute("href");
			if (!href) return;
			if (e.button !== 0 && e.button !== 1) return;
			e.preventDefault();
			const background =
				e.button === 1 || e.ctrlKey || e.metaKey || e.shiftKey;
			chrome.tabs.create({
				url: new URL(href, "https://otodb.net/").toString(),
				active: !background,
			});
			if (!background) window.close();
		}
		document.addEventListener("click", handleLinkClick);
		document.addEventListener("auxclick", handleLinkClick);
	});
</script>

<div class="text-otodb-content-primary h-full {themeClass}">
	<div class="bg-marker bg-otodb-bg-primary fixed inset-0 -z-10"></div>
	{@render children()}
</div>
