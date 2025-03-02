<script lang="ts">
	import { base } from '$app/paths';
	import type { components } from './schema';

    interface Props {
        tag: components['schemas']['TagWorkSchema'];
    }
    const { tag }: Props = $props();
</script>

<a href="{base}/tag/{tag.slug}" class="rounded-full border border-solid px-2 {
    ['border-white-600', 'border-indigo-600', 'border-orange-600', 'border-yellow-600', 'border-red-600', 'border-cyan-600'][tag.category]
}">{tag.name}</a>

<style>

</style>
