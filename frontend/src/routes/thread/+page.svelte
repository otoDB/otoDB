<script lang="ts">
	import Section from '$lib/Section.svelte';
	import ThreadTable from '$lib/ThreadTable.svelte';

	import { m } from '$lib/paraglide/messages.js';
	import Pager from '$lib/Pager.svelte';
	import { PostCategory } from '$lib/schema.js';
	import { enumValues } from '$lib/enums.js';
	import { postCategoryNames } from '$lib/enums/postCategory.js';
	import { page } from '$app/state';

	let { data } = $props();
</script>

<Section
	title={m.just_salty_anaconda_nourish()}
	type={m.mean_top_antelope_love()}
	menuLinks={data.links}
>
	<form target="_self" method="get">
		<label class="block"
			>{m.plane_awful_bobcat_spark()}
			<select name="category" value={data.category ?? -1}>
				<option value={-1}>{m.keen_soft_crow_relish()}</option>
				{#each enumValues(PostCategory) as c (c)}
					<option value={c}>{postCategoryNames[c]()}</option>
				{/each}
			</select>
		</label>
		<input
			type="text"
			name="query"
			placeholder="{m.mean_top_antelope_love()}..."
			value={data.query}
		/>
		<input type="submit" />
	</form>
	<hr class="my-5" />

	<ThreadTable posts={data.results.items} showCategory />
	<Pager n_count={data.results.count} page_size={data.batch_size} base_url={page.url.toString()} />
</Section>
