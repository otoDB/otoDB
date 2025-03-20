<script lang="ts">
	import { Platform } from "./enums";
	import type { components } from "./schema";


interface Props {
    src: components['schemas']['WorkSourceSchema']
}

let { src }: Props = $props();
</script>

{#if src.platform === 1}
<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/{src.source_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
{:else if src.platform === 2}
<iframe src="https://embed.nicovideo.jp/watch/{src.source_id}" allowfullscreen scrolling="no" allow="encrypted-media;" title="Niconico Player"></iframe>
{:else if src.platform === 3}
<iframe src="//player.bilibili.com/player.html?isOutside=true&bvid={src.source_id}&p=1" scrolling="no" frameborder="no" allowfullscreen title="bilibili Player"></iframe>
{/if}
