<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import type { PageProps } from './$types';
	let { data }: PageProps = $props();
	import { m } from '$lib/paraglide/messages.js';
	import { LanguageNames, PostCategories } from '$lib/enums';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import Markdown from 'svelte-exmarkdown';

	let md = $state('');
</script>

<Section title={m.antsy_aloof_horse_grace()} menuLinks={data.links}>
	<form method="POST" use:enhance>
		<table>
			<tbody
				><tr
					><th>{m.large_factual_octopus_exhale()}</th><td
						><input type="text" name="title" required /></td
					></tr
				><tr
					><th>{m.hour_loud_squirrel_ascend()}</th><td
						><select name="lang" value={getLocale()}>
							{#each locales as l, i (i)}
								<option value={l}>{LanguageNames[l]}</option>
							{/each}
						</select></td
					></tr
				><tr
					><th>{m.plane_awful_bobcat_spark()}</th><td
						><select name="category" value={data.category ?? '1'}>
							{#each PostCategories as c, i (i)}
								{#if i > 0}
									<option value={i.toString()}>{c()}</option>
								{/if}
							{/each}
						</select></td
					></tr
				></tbody
			>
		</table>
		<div class="grid grid-cols-2 gap-3">
			<textarea rows="10" bind:value={md} class="w-full" name="post" required></textarea>
			<div class="prose prose-neutral prose-sm dark:prose-invert">
				<Markdown {md} />
			</div>
		</div>
		<input type="submit" />
	</form>
</Section>
