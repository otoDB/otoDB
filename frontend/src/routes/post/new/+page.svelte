<script lang="ts">
	import { enhance } from '$app/forms';
	import Section from '$lib/Section.svelte';
	import { buildEntityRoutes, enumValues } from '$lib/enums';
	import { languages } from '$lib/enums/language.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { get_entity, renderMarkdown } from '$lib/markdown';
	import { m } from '$lib/paraglide/messages.js';
	import { getLocale, locales } from '$lib/paraglide/runtime';
	import { PostCategory } from '$lib/schema.js';

	let { data } = $props();
	let md = $state('');
	let previewHtml = $derived(renderMarkdown(md));
	let category: PostCategory = $derived(data.category ?? PostCategory.Bug_Report);
	let entities_raw = $derived(data.entity ?? '');
	let entities = $derived(
		entities_raw
			.split('\n')
			.map(get_entity)
			.filter((x) => !!x)
	);
</script>

<Section title={m.antsy_aloof_horse_grace()} menuLinks={data.links}>
	<form method="POST" use:enhance>
		<table>
			<tbody
				><tr
					><th>{m.large_factual_octopus_exhale()}</th><td
						><input
							type="text"
							name="title"
							required
							autocomplete="off"
							value={data.title}
						/></td
					></tr
				><tr
					><th>{m.hour_loud_squirrel_ascend()}</th><td
						><select name="lang" value={getLocale()}>
							{#each locales as l, i (i)}
								<option value={l}>{languages[l].name}</option>
							{/each}
						</select></td
					></tr
				><tr
					><th>{m.plane_awful_bobcat_spark()}</th><td
						><select name="category" bind:value={category}>
							{#each enumValues(PostCategory) as c, i (i)}
								{#if c !== PostCategory.Announcement}
									<option value={c}>{postCategoryNames[c]()}</option>
								{/if}
							{/each}
						</select></td
					></tr
				></tbody
			>
		</table>
		{#if category === PostCategory.Gardening}
			<h4>{m.fine_zany_octopus_trim()}</h4>
			<textarea name="entities" bind:value={entities_raw}></textarea>
			<ul class="inline-block">
				{#each entities as { entity, id }, i (i)}
					{@const link = buildEntityRoutes(entity, id)}
					<li>
						<a href={link}>{link}</a>
					</li>
				{/each}
			</ul>
		{/if}
		<div class="grid grid-cols-2 gap-3">
			<textarea rows="10" bind:value={md} class="w-full" name="post" required></textarea>
			<div class="prose prose-neutral prose-sm dark:prose-invert">
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html previewHtml}
			</div>
		</div>
		<input type="submit" />
	</form>
</Section>
