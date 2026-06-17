<script lang="ts">
	import { Platform, type components } from '$lib/schema';

	interface Props {
		src: components['schemas']['WorkSourceSchema'];
		width?: number;
		height?: number;
		autoplay?: boolean;
	}

	let { src, width = 560, height = 315, autoplay = true }: Props = $props();
</script>

{#if src.platform === Platform.YouTube}
	<iframe
		{width}
		{height}
		src="https://www.youtube-nocookie.com/embed/{src.source_id}{autoplay ? '?autoplay=1' : ''}"
		title="YouTube video player"
		frameborder="0"
		allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
		referrerpolicy="strict-origin-when-cross-origin"
		allowfullscreen
	></iframe>
{:else if src.platform === Platform.Niconico}
	<iframe
		{width}
		{height}
		src="https://embed.nicovideo.jp/watch/{src.source_id}{autoplay ? '?autoplay=1' : ''}"
		allowfullscreen
		scrolling="no"
		allow="encrypted-media;"
		title="Niconico Player"
	></iframe>
{:else if src.platform === Platform.Bilibili}
	<iframe
		{width}
		{height}
		src="//player.bilibili.com/player.html?isOutside=true&bvid={src.source_id}&p={autoplay ? 1 : 0}"
		scrolling="no"
		frameborder="no"
		allowfullscreen
		title="Bilibili Player"
	></iframe>
{:else if src.platform === Platform.SoundCloud}
	<iframe
		title="SoundCloud Player"
		{width}
		{height}
		scrolling="no"
		frameborder="no"
		allow="autoplay"
		src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{src.source_id}&visual=true&auto_play={autoplay}"
	></iframe>
{:else if src.platform === Platform.Twitter}
	<iframe
		title="Twitter Embed"
		loading="lazy"
		{width}
		height={Math.round(width / (src.work_width! / src.work_height!)) || height}
		src="https://platform.twitter.com/embed/Tweet.html?dnt=true&embedId=twitter-widget-0&frame=false&hideCard=true&hideThread=true&id={src.source_id}&maxWidth={width}px&origin={encodeURIComponent(
			window.location.origin
		)}&width={width}px"
		frameborder="0"
		scrolling="no"
	></iframe>
{:else if src.platform === Platform.AcFun}
	<iframe
		title="AcFun Player"
		{width}
		{height}
		src="https://www.acfun.cn/player/{src.source_id}"
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
