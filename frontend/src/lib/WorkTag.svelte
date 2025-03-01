<script lang="ts">
	import { base } from '$app/paths';

    const { tag } = $props();
</script>

<a href="{base}/tag/{tag.slug}" class="rounded-full border border-solid px-2 border-{
    ['white', 'indigo', 'orange', 'yellow', 'red', 'cyan'][tag.category]
}-600">{tag.name}</a>

<style>

</style>
