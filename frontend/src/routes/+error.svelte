<script lang="ts">
	import { page } from '$app/state';
	import Banner from '$lib/Banner.svelte';
	import Section from '$lib/Section.svelte';
	import { m } from '$lib/paraglide/messages.js';
</script>

<Section title={m.careful_gross_husky_grasp()}>
	<Banner variant="danger" title={`${page.status}`}>
		<p>{page.error?.message ?? m.ideal_soft_falcon_urge()}</p>
		{#if page.status === 404}
			<img src="/404.png" alt="" class="mx-auto mb-3 block w-full max-w-xs" />
		{/if}
	</Banner>
</Section>
