<script lang="ts">
	import { base } from '$app/paths';
	import type { components } from './schema';
	import WorkTag from './WorkTag.svelte';

    interface Props {
        work: components['schemas']['WorkSchema'];
        width: number;
    };
    const { work, width = 200 }: Props = $props();
</script>

<div class="card relative" style="width:{width}px;">
    <div style="width:{width}px;height:{200/16*9}px;" class="overflow-hidden">
        <a href="{base}/work/{work.id}">
            <img src={work.thumbnail} alt={work.title}>
        </a>
    </div>
    <a href="{base}/work/{work.id}">{work.title}</a>
    <div class="hidden absolute tags w-full z-1 gap-1 flex-wrap">
        {#each work.tags as tag}
        <WorkTag {tag} />
        {/each}
    </div>
</div>

<style>
.card {
    background-color: var(--otodb-bg-color);
    > .tags {
        background-color: var(--otodb-bg-color);
    }
    &:hover > .tags {
        display: flex;
    }
}
</style>
