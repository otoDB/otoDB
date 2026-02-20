<script lang="ts">
	import type { components } from './schema';

	interface Props {
		src: components['schemas']['WorkSourceSchema'];
		width: number;
		height: number;
	}

	let { src, width = 560, height = 315 }: Props = $props();
</script>

{#if src.platform === 1}
	<iframe
		{width}
		{height}
		src="https://www.youtube-nocookie.com/embed/{src.source_id}"
		title="YouTube video player"
		frameborder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		referrerpolicy="strict-origin-when-cross-origin"
		allowfullscreen
	></iframe>
{:else if src.platform === 2}
	<iframe
		{width}
		{height}
		src="https://embed.nicovideo.jp/watch/{src.source_id}"
		allowfullscreen
		scrolling="no"
		allow="encrypted-media;"
		title="Niconico Player"
	></iframe>
{:else if src.platform === 3}
	<iframe
		{width}
		{height}
		src="//player.bilibili.com/player.html?isOutside=true&bvid={src.source_id}&p=1"
		scrolling="no"
		frameborder="no"
		allowfullscreen
		title="Bilibili Player"
	></iframe>
{:else if src.platform === 4}
	<iframe
		title="SoundCloud Player"
		{width}
		{height}
		scrolling="no"
		frameborder="no"
		allow="autoplay"
		src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{src.source_id}&visual=true"
	></iframe>
{:else if src.platform === 5}
	<iframe
		title="Twitter Embed"
		loading="lazy"
		{width}
		{height}
		src="https://platform.twitter.com/embed/Tweet.html?dnt=true&embedId=twitter-widget-0&frame=false&hideCard=true&hideThread=true&id={src.source_id}&maxWidth={width}px&origin={encodeURIComponent(
			window.location.origin
		)}&width={width}px"
		frameborder="0"
		scrolling="no"
	></iframe>
{:else if src.platform === 6}
	<iframe
		title="AcFun Player"
		{width}
		{height}
		src="https://www.acfun.cn/player/ac{src.source_id}"
		frameborder="no"
		scrolling="no"
		allowfullscreen
	></iframe>
{/if}

<style>
	iframe {
		max-width: 100%;
	}
</style>
