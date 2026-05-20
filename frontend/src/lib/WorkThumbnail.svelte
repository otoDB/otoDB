<script lang="ts">
	interface Props {
		thumbnail: string | null | undefined;
		alt: string;
		class?: string;
	}
	const { thumbnail, alt, ...props }: Props = $props();
</script>

{#if thumbnail}
	<img src={thumbnail} {alt} class={[props.class]} />
{:else}
	<div
		class={[
			'bg-otodb-bg-primary text-otodb-content-fainter missing-thumbnail flex flex-col items-center justify-center',
			props.class
		]}
	>
		<span class="icon-[gravity-ui--picture] size-16" aria-hidden="true"></span>
	</div>
{/if}

<style>
	.missing-thumbnail {
		background: repeating-linear-gradient(45deg, var(--color-otodb-bg-primary) 0px 32px, var(--color-otodb-bg-faint) 32px 64px);
	}
</style>
