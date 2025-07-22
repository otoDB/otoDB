<script lang="ts">
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, setLocale } from '$lib/paraglide/runtime';

	import { background } from '$lib/stores/theme';
	import { LanguageNames } from '$lib/enums';

	function changeBackground(newTheme: string) {
		return () => background.set(newTheme);
	}
</script>

<Section title={m.orange_born_seal_ascend()}>
	<h2 class="text-lg">{m.hour_loud_squirrel_ascend()}</h2>
	<div class="mt-4 grid grid-cols-4 gap-8">
		{#each ['en', 'ja', 'ko', 'zh-cn'] as const as key (key)}
			<button
				aria-pressed={getLocale() === key}
				onclick={() => setLocale(key)}
				class="bg-otodb-bg-faint aria-pressed:bg-otodb-bg-fainter hover:bg-otodb-bg-fainter mb-2 cursor-pointer px-4 py-4 text-lg"
			>
				{LanguageNames[key]}
			</button>
		{/each}
	</div>

	<hr class="my-8" />

	<h2 class="text-lg">{m.acidic_sound_opossum_bump()}</h2>
	<div
		class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5"
	>
		<button onclick={changeBackground('none')}>
			<div class="h-48 bg-black"></div>
			<div class="py-2 text-lg">{m.grassy_noble_walrus_wish()}</div>
		</button>
		<button onclick={changeBackground('aniki')}>
			<img
				alt="aniki"
				src="/aniki-bg.png"
				class="h-48 w-full object-cover object-left object-top"
			/>
			<div class="py-2 text-lg">{m.next_ago_opossum_swim()}</div>
		</button>
	</div>
</Section>
