<script lang="ts">
	import * as v from 'valibot';
	import ConnectionFavicon from '$lib/ConnectionFavicon.svelte';
	import Icon from '$lib/Icon/Icon.svelte';
	import { m } from '$lib/paraglide/messages';
	import { extractUrl } from './extractUrl';

	const URL_SCHEMA = v.pipe(v.string(), v.trim(), v.url());

	interface Row {
		url: string;
		origin: 'existing' | 'new';
		removed: boolean;
	}

	interface Props {
		urls: string[];
	}

	let { urls = $bindable() }: Props = $props();

	// Snapshot the incoming urls once: this component owns the list from here on,
	// so existing entries can be flagged for removal (and undone) instead of deleted outright.
	let rows: Row[] = $state(urls.map((url) => ({ url, origin: 'existing', removed: false })));

	$effect(() => {
		urls = rows.filter((row) => !row.removed).map((row) => row.url);
	});

	let draft = $state('');
	const draftFaviconKey = $derived(extractUrl(draft));
	const isDraftValid = $derived(v.safeParse(URL_SCHEMA, draft).success);

	const confirm = () => {
		const result = v.safeParse(URL_SCHEMA, draft);
		if (!result.success) return;

		rows = [...rows, { url: result.output, origin: 'new', removed: false }];
		draft = '';
	};

	// A newly added row can just be deleted outright; an existing row is only flagged,
	// so an accidental click can still be undone before the surrounding form is submitted.
	const remove = (i: number) => {
		rows =
			rows[i].origin === 'new'
				? rows.filter((_, index) => index !== i)
				: rows.map((row, index) => (index === i ? { ...row, removed: true } : row));
	};

	const restore = (i: number) => {
		rows = rows.map((row, index) => (index === i ? { ...row, removed: false } : row));
	};
</script>

<div class="flex flex-col gap-y-2">
	{#each rows as row, i (i)}
		{@const faviconKey = extractUrl(row.url)}
		<div class="flex items-center gap-x-2">
			<div class="size-4 shrink-0">
				{#if faviconKey}
					<ConnectionFavicon type={faviconKey} class="size-full" />
				{:else}
					<Icon key="external-link" class="size-full" />
				{/if}
			</div>
			<input
				type="text"
				value={row.url}
				readonly
				class={['w-full px-2 font-mono', row.removed && 'text-gray-400 line-through']}
			/>
			{#if row.removed}
				<button
					type="button"
					class="px-2"
					aria-label={m.quiet_plain_otter_return()}
					onclick={() => restore(i)}
				>
					<Icon key="list-restore" class="size-4" />
				</button>
			{:else}
				<button
					type="button"
					class="px-2"
					aria-label={m.even_alert_grebe_taste()}
					onclick={() => remove(i)}
				>
					<Icon key="list-remove" class="size-4" />
				</button>
			{/if}
		</div>
	{/each}

	<div class="flex items-center gap-x-2">
		<div class="size-4 shrink-0">
			{#if draftFaviconKey}
				<ConnectionFavicon type={draftFaviconKey} class="size-full" />
			{:else}
				<Icon key="external-link" class="size-full" />
			{/if}
		</div>
		<input type="text" bind:value={draft} class="w-full px-2 font-mono" />
		<button
			type="button"
			class="px-2"
			aria-label={m.spare_kind_otter_gain()}
			disabled={!isDraftValid}
			onclick={confirm}
		>
			<Icon key="list-add" class="size-4" />
		</button>
	</div>
</div>
