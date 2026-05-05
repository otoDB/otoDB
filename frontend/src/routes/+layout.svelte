<script lang="ts">
	import { afterNavigate, beforeNavigate } from '$app/navigation';
	import { page } from '$app/state';
	import Banner from '$lib/Banner.svelte';
	import Footer from '$lib/Footer.svelte';
	import GlobalSideNav from '$lib/GlobalSideNav/GlobalSideNav.svelte';
	import Section from '$lib/Section.svelte';
	import { isFormDirty } from '$lib/dirty';
	import { languages, resolveLanguageKeyById } from '$lib/enums/language';
	import type { ErrorPayload } from '$lib/errors';
	import { m } from '$lib/paraglide/messages.js';
	import { defineCustomClientStrategy } from '$lib/paraglide/runtime';
	import { ThemePref } from '$lib/schema';
	import { themes } from '$lib/themes/themes';
	import { callApiErrorToast, callErrorToast } from '$lib/toast';
	import { getLocalPref, getLocalPrefs, updateLocalPref } from '$lib/ui';
	import { Toaster } from 'svelte-sonner';
	import '../app.css';

	let { data, children } = $props();

	defineCustomClientStrategy('custom-userPreference', {
		getLocale: () => {
			const lang = data.user?.prefs.LANGUAGE ?? getLocalPrefs()?.LANGUAGE; // Don't want our default behaviour here
			return lang ? resolveLanguageKeyById(lang) : undefined;
		},
		setLocale: (locale) => {
			if (!data.user)
				updateLocalPref('LANGUAGE', languages[locale as keyof typeof languages].id);
		}
	});

	$effect(() => {
		const f = page.form;
		if (
			f &&
			typeof f === 'object' &&
			'failed' in f &&
			f.failed === true &&
			'code' in f &&
			typeof f.code === 'number'
		) {
			callApiErrorToast({
				code: f.code,
				data: 'errorData' in f ? (f.errorData as ErrorPayload) : null
			});
		}
	});

	function handleError(e: Event) {
		const err = e as ErrorEvent;
		console.error(err.error ?? err.message);
		callErrorToast(m.ideal_soft_falcon_urge());
	}

	function handleRejection(e: PromiseRejectionEvent) {
		console.error(e.reason);
		callErrorToast(m.ideal_soft_falcon_urge());
	}

	let boundaryError: unknown = $state(null);
	let boundaryReset: () => void = $state(() => {});

	function handleBoundaryError(e: unknown, reset: () => void) {
		console.error(e);
		boundaryError = e;
		boundaryReset = reset;
	}

	let isMobileNavOpen = $state(false);
	function toggleMobileNav() {
		isMobileNavOpen = !isMobileNavOpen;
	}
	function closeMobileNav() {
		isMobileNavOpen = false;
	}
	beforeNavigate(({ cancel, type }) => {
		if (
			type !== 'form' &&
			type !== 'goto' &&
			Array.from(document.querySelectorAll('form')).some(isFormDirty)
		)
			if (!confirm(m.raw_actual_mallard_exhale())) cancel();
	});
	afterNavigate(() => {
		if (boundaryError) {
			boundaryError = null;
			boundaryReset();
		}
	});

	const ldTag = (json: string) => '<script type="application/ld+json">' + json + '</' + 'script>';

	const organizationLd = ldTag(
		JSON.stringify({
			'@context': 'https://schema.org',
			'@type': 'Organization',
			'name': 'otoDB',
			'url': 'https://otodb.net',
			'sameAs': ['https://twitter.com/otoDBnet', 'https://github.com/otoDB']
		})
	);

	const breadcrumbLd = $derived(
		page.data.head?.breadcrumbs
			? ldTag(
					JSON.stringify({
						'@context': 'https://schema.org',
						'@type': 'BreadcrumbList',
						'itemListElement': (
							page.data.head.breadcrumbs as { name: string; url: string }[]
						).map(
							(
								crumb: { name: string; url: string },
								i: number,
								arr: { name: string; url: string }[]
							) => ({
								'@type': 'ListItem',
								'position': i + 1,
								'name': crumb.name,
								...(i < arr.length - 1
									? { item: `https://otodb.net${crumb.url}` }
									: {})
							})
						)
					})
				)
			: null
	);

	// theme switcher
	$effect(() => {
		document.documentElement.setAttribute(
			'data-theme',
			themes[data.user?.prefs?.THEME ?? getLocalPref('THEME') ?? ThemePref.Default].key
		);
	});
</script>

<svelte:window onerror={handleError} onunhandledrejection={handleRejection} />

<svelte:head>
	{#if page.data.head?.title}
		<title>{page.data.head.title} | otoDB</title>
		<meta property="og:title" content={page.data.head.title} />
		<meta name="twitter:title" content={page.data.head.title} />
	{:else}
		<title>otoDB</title>
		<meta property="og:title" content="otoDB" />
		<meta name="twitter:title" content="otoDB" />
	{/if}
	{#if page.data.head?.description}
		<meta name="description" content={page.data.head.description} />
		<meta property="og:description" content={page.data.head.description} />
		<meta name="twitter:description" content={page.data.head.description} />
	{/if}
	{#if page.data.head?.image}
		<meta property="og:image" content={page.data.head.image} />
		<meta name="twitter:image" content={page.data.head.image} />
	{:else}
		<meta property="og:image" content="https://otodb.net/thumb.png" />
		<meta name="twitter:image" content="https://otodb.net/thumb.png" />
	{/if}
	<meta property="og:type" content={page.data.head?.ogType ?? 'website'} />
	<link rel="canonical" href="{page.url.origin}{page.url.pathname}" />
	<meta property="og:url" content="{page.url.origin}{page.url.pathname}" />
	<meta name="twitter:card" content="summary_large_image" />
	{#if page.data.head?.isExplicit}
		<meta name="rating" content="adult" />
	{/if}
	<!-- eslint-disable-next-line svelte/no-at-html-tags -->
	{@html organizationLd}
	{#if breadcrumbLd}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -->
		{@html breadcrumbLd}
	{/if}
</svelte:head>

<a href="#content" class="absolute z-50 transform-[translateY(-100%)] focus:transform-none">
	{m.round_extra_impala_fry()}
</a>

<div class="text-otodb-content-primary overflow-auto">
	<div id="bg-marker" class="bg-otodb-bg-primary fixed h-lvh w-full"></div>
	<div class="contents md:hidden">
		<!-- Hamburger button -->
		<button
			class={[
				'bg-otodb-bg-primary/90 fixed bottom-[32px] left-[32px] z-[3] h-12 w-12',
				{ invisible: isMobileNavOpen }
			]}
			onclick={toggleMobileNav}
		>
			<div class="white place-self-center text-2xl">☰</div>
		</button>
	</div>
	<Toaster
		expand={true}
		position="bottom-right"
		toastOptions={{
			unstyled: true,
			classes: {
				toast: 'bg-otodb-bg-faint text-otodb-content-color flex p-2 gap-3 border-otodb-fainter-content border'
			}
		}}
	/>
	<header class="relative col-span-2 px-6 py-16 md:px-48">
		<address class="font-mono text-2xl italic">
			<a href="/" class="no-underline!">
				{m.mild_loud_shad_enchant({ type: 'otoDB', name: m.glad_born_mouse_taste() })}
			</a>
		</address>
	</header>

	<div class="relative mx-auto w-full gap-x-4 px-4 md:flex">
		<div
			class={[
				'fixed top-0 left-0 z-2 size-full md:pointer-events-auto md:relative md:size-auto md:bg-transparent',
				isMobileNavOpen ? 'bg-otodb-bg-primary/90' : 'pointer-events-none bg-transparent'
			]}
		>
			<GlobalSideNav user={data.user} {isMobileNavOpen} {closeMobileNav} stats={data.stats} />
		</div>
		<div class="grow">
			<main id="content">
				<svelte:boundary onerror={handleBoundaryError}>
					{@render children()}
					{#snippet failed()}
						<Section title={m.careful_gross_husky_grasp()}>
							<Banner variant="danger" title={m.key_pink_pigeon_treasure()}>
								<p>{m.ideal_soft_falcon_urge()}</p>
							</Banner>
						</Section>
					{/snippet}
				</svelte:boundary>
			</main>
			<Footer user={data.user}></Footer>
		</div>
	</div>
</div>
