<script lang="ts">
	import WorkThumbnail from '$lib/WorkThumbnail/WorkThumbnail.svelte';
	import ExternalEmbed from '$lib/ExternalEmbed.svelte';
	import { PlatformNames, WorkOriginNames } from '$lib/enums';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocalPrefs } from '$lib/ui';
	import { Platform, VideoPlatformPref, WorkOrigin, type components } from '$lib/schema';

	type Source = components['schemas']['WorkSourceSchema'];

	interface Props {
		sources: Source[];
		thumbnail?: string | null;
		thumbnailAlt?: string;
		width?: number;
		height?: number;
		user: App.Locals['user'];
	}

	let {
		sources,
		thumbnail = null,
		thumbnailAlt = '',
		width = 480,
		height = 270,
		user
	}: Props = $props();

	// Earliest published_date first; sources without a date sort last
	function byDateAsc(a: Source, b: Source): number {
		const da = a.published_date;
		const db = b.published_date;
		if (da == null && db == null) return 0;
		if (da == null) return 1;
		if (db == null) return -1;
		return da < db ? -1 : da > db ? 1 : 0;
	}

	// Index of the source to play. With a specific platform preferred: author upload on that
	// platform -> (if "prefer author uploads" is on) oldest author upload anywhere -> reupload on
	// that platform. Otherwise/falling through: author by oldest date -> reupload by oldest date ->
	// first available (-1 if none).
	function selectPreferredSource(
		candidates: Source[],
		platformPref: VideoPlatformPref,
		preferAuthor: boolean
	): number {
		if (candidates.length === 0) return -1;

		const indices = candidates.map((_, i) => i);
		const authors = indices
			.filter((i) => candidates[i].work_origin === WorkOrigin.Author)
			.sort((a, b) => byDateAsc(candidates[a], candidates[b]));
		const reuploads = indices
			.filter((i) => candidates[i].work_origin === WorkOrigin.Reupload)
			.sort((a, b) => byDateAsc(candidates[a], candidates[b]));

		if (platformPref !== VideoPlatformPref.Auto) {
			const platform = platformPref as unknown as Platform;
			const authorOnPlatform = authors.find((i) => candidates[i].platform === platform);
			if (authorOnPlatform !== undefined) return authorOnPlatform;
			if (preferAuthor && authors.length > 0) return authors[0];
			const reuploadOnPlatform = reuploads.find((i) => candidates[i].platform === platform);
			if (reuploadOnPlatform !== undefined) return reuploadOnPlatform;
		}

		if (authors.length > 0) return authors[0];
		if (reuploads.length > 0) return reuploads[0];
		return 0;
	}

	let selected = $state(-1);

	$effect(() => {
		void sources;
		selected = -1;
	});

	let visibleSources = $derived(sources.filter((s) => s.work_status !== 1));

	let local_prefs = $derived(getLocalPrefs());
	let preferredIndex = $derived(
		selectPreferredSource(
			visibleSources,
			user?.prefs.VIDEO_PLATFORM ?? local_prefs.VIDEO_PLATFORM,
			user?.prefs.PREFER_AUTHOR_UPLOAD ?? local_prefs.PREFER_AUTHOR_UPLOAD
		)
	);
</script>

{#if selected === -1}
	<div class="relative h-[270px] w-[480px] max-w-full">
		<WorkThumbnail {thumbnail} alt={thumbnailAlt} class="h-[270px] w-[480px] object-cover" />
		{#if preferredIndex !== -1}
			<button type="button" class="play_overlay" onclick={() => (selected = preferredIndex)}>
				<span class="play">
					<span class="icon-[gravity-ui--play-fill] size-2.5" aria-hidden="true"></span>
					{m.wise_calm_otter_play()}
				</span>
			</button>
		{/if}
	</div>
{:else}
	<ExternalEmbed {width} {height} src={visibleSources[selected]} />
{/if}
<div class="my-2 max-w-[480px]">
	<a
		href={thumbnail}
		target="_blank"
		rel="noopener noreferrer"
		class="cover_select"
		class:selected={selected === -1}
		onclick={(e) => {
			e.preventDefault();
			selected = -1;
		}}
	>
		{m.heroic_ideal_orangutan_aid()}
	</a>{#each visibleSources as s, i (i)}<a
			href={s.url}
			target="_blank"
			rel="noopener noreferrer"
			class="cover_select"
			class:selected={selected === i}
			onclick={(e) => {
				e.preventDefault();
				selected = i;
			}}
		>
			{PlatformNames[s.platform]}{s.work_origin === WorkOrigin.Author
				? ''
				: ' ' + WorkOriginNames[s.work_origin]()}
		</a>{/each}
</div>

<style>
	.play_overlay {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: flex-end;
		justify-content: flex-end;
		padding: 0.5rem;
		border: none;
		cursor: pointer;
		background-color: transparent;

		& .play {
			display: flex;
			align-items: center;
			gap: 0.3rem;
			padding: 0.2rem 0.5rem;
			background-color: var(--otodb-color-bg-primary);
			border: 1px solid var(--otodb-color-content-primary);
		}

		&:hover .play,
		&:focus-visible .play {
			background-color: var(--otodb-color-bg-fainter);
		}

		&:active .play {
			background-color: var(--otodb-color-bg-faint);
		}
	}

	.cover_select {
		padding: 0.2rem 0.5rem;
		display: inline-block;
		background-color: var(--otodb-color-bg-primary);
		border: 1px solid var(--otodb-color-content-primary);
		text-decoration: none;
		&:hover {
			background-color: var(--otodb-color-bg-fainter);
		}
		&:active {
			background-color: var(--otodb-color-bg-faint);
		}
		&.selected {
			background-color: var(--otodb-color-content-primary);
			border: 1px solid var(--otodb-color-bg-primary);
			color: var(--otodb-color-bg-primary);
		}
	}
</style>
