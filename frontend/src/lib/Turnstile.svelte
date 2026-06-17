<script lang="ts" module>
	// https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/
	type TurnstileApi = {
		render: (
			container: HTMLElement,
			params: { sitekey: string; action?: string }
		) => string | undefined;
		reset: (widgetId?: string) => void;
		remove: (widgetId: string) => void;
	};

	const turnstileApi = () => (window as { turnstile?: TurnstileApi }).turnstile;

	let apiLoading: Promise<void> | undefined;

	const loadTurnstileApi = () => {
		if (turnstileApi()) return Promise.resolve();
		apiLoading ??= new Promise<void>((resolve) => {
			const script = document.createElement('script');
			script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
			script.defer = true;
			script.addEventListener('load', () => resolve());
			document.head.appendChild(script);
		});
		return apiLoading;
	};
</script>

<script lang="ts">
	import { page } from '$app/state';
	import { env } from '$env/dynamic/public';
	import type { Attachment } from 'svelte/attachments';

	type Props = {
		action: string;
	};

	const { action }: Props = $props();

	const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY;

	let widgetId: string | undefined;

	const turnstile: Attachment<HTMLDivElement> = (element) => {
		if (!siteKey) return;
		let detached = false;
		void loadTurnstileApi().then(() => {
			if (!detached) widgetId = turnstileApi()?.render(element, { sitekey: siteKey, action });
		});
		return () => {
			detached = true;
			if (widgetId) {
				turnstileApi()?.remove(widgetId);
				widgetId = undefined;
			}
		};
	};

	let lastForm = page.form;
	$effect(() => {
		if (page.form !== lastForm) {
			lastForm = page.form;
			if (widgetId) turnstileApi()?.reset(widgetId);
		}
	});
</script>

{#if siteKey}
	<div {@attach turnstile}></div>
{/if}
