<script lang="ts">
	import { navigating } from '$app/state';

	let { active }: { active?: boolean } = $props();

	const loading = $derived(active ?? navigating.to !== null);
</script>

{#if loading}
	<div
		class="loading-indicator [--trail-duration:1s] [--trail-width:66.667vw] md:[--trail-duration:0.6s] md:[--trail-width:40vw]"
		role="status"
	></div>
{/if}

<style>
	.loading-indicator {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 40;
		height: 3px;
		background-image: linear-gradient(to right, transparent, var(--otodb-color-content-primary));
		background-repeat: repeat-x;
		background-size: var(--trail-width) 100%;
		animation: loading-trail var(--trail-duration) linear infinite;
	}

	@keyframes loading-trail {
		from {
			background-position-x: 0;
		}
		to {
			background-position-x: var(--trail-width);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.loading-indicator {
			background-image: none;
			background-color: var(--otodb-color-content-primary);
			animation: loading-pulse 1.4s ease-in-out infinite;
		}

		@keyframes loading-pulse {
			50% {
				opacity: 0.25;
			}
		}
	}
</style>
