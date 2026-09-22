<script lang="ts">
	import { onMount } from "svelte";
	import { languages } from "$lib/enums/language";
	import {
		defineCustomClientStrategy,
		setLocale,
	} from "$lib/paraglide/runtime";
	import { ThemePref } from "$lib/schema";
	import { themes } from "$lib/themes/themes";
	import Popup from "./Popup.svelte";
	import "./styles.css";

	const CACHE = "otodb.theme";

	let resolvedLang: keyof typeof languages | undefined = $state(undefined);
	let themeKey = $state(
		localStorage.getItem(CACHE) ?? themes[ThemePref.Default].key,
	);

	$effect(() => {
		document.documentElement.setAttribute("data-theme", themeKey);
	});

	defineCustomClientStrategy("custom-userPreference", {
		getLocale: () => resolvedLang,
		setLocale: () => {},
	});

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

	type Prefs = { LANGUAGE?: number | null; THEME?: ThemePref | null };

	async function fetchAuthPrefs(): Promise<Prefs | undefined> {
		try {
			const res = await window.fetch(
				"https://otodb.net/api/auth/status",
				{ credentials: "include" },
			);
			if (!res.ok) return undefined;
			const body = (await res.json()) as { prefs?: Prefs };
			return body.prefs;
		} catch {
			return undefined;
		}
	}

	onMount(async () => {
		const [fallbackLocale, { prefs: anonPrefs }, serverPrefs] =
			await Promise.all([
				pickDefaultLocale(),
				chrome.storage.local.get("prefs") as Promise<{
					prefs?: Prefs;
				}>,
				fetchAuthPrefs(),
			]);
		const prefs = serverPrefs ?? anonPrefs;

		resolvedLang = langKeyById(prefs?.LANGUAGE) ?? fallbackLocale;
		if (resolvedLang) setLocale(resolvedLang, { reload: false });

		themeKey = themes[prefs?.THEME ?? ThemePref.Default].key;
		localStorage.setItem(CACHE, themeKey);
	});

	// Frontend components link with site-relative paths like `/tag/foo` which
	// would otherwise resolve to chrome-extension://.../tag/foo
	function resolveLink(e: MouseEvent) {
		const a = (e.target as HTMLElement | null)?.closest("a");
		const href = a?.getAttribute("href");
		if (!a || !href) return;
		a.href = new URL(href, "https://otodb.net/").toString();
		a.target = "_blank";
	}
</script>

<svelte:window onclick={resolveLink} onauxclick={resolveLink} />

<div class="text-otodb-content-primary h-full">
	<div id="bg-marker" class="bg-otodb-bg-primary fixed inset-0 -z-10"></div>
	<Popup />
</div>
