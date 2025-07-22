<script lang="ts">
	import type { PageProps } from '../$types';
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';

	import { background } from '$lib/stores/theme';

	function changeBackground(newTheme: string) {
		return () => background.set(newTheme);
	}
</script>

<Section title={m.orange_born_seal_ascend()}>
	<h2 class="mt-8 text-lg">{m.acidic_sound_opossum_bump()}</h2>
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
