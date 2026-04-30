<script lang="ts">
	import { page } from '$app/state';
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
</script>

<Section title={m.careful_gross_husky_grasp()}>
	<div class="mx-[10%] my-1 border border-red-700 bg-red-950/50 p-4 text-left">
		<h2 class="mb-1 text-lg font-bold">
			{page.status}
		</h2>
		<p>{page.error?.message ?? m.ideal_soft_falcon_urge()}</p>
	</div>
</Section>
