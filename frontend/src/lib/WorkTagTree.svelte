<script lang="ts">
	import type { ComponentProps } from 'svelte';
	import WorkTag from '$lib/WorkTag.svelte';

	type Tree = {
		node: ComponentProps<typeof WorkTag>['tag'];
		children?: Tree[];
		real: boolean;
	};

	interface Props {
		tree: Tree;
		onClickTag?: ComponentProps<typeof WorkTag>['onclick'];
	}
	const { tree, onClickTag }: Props = $props();
</script>

{#snippet recur(tree: Tree)}
	<ul class="my-0.5 list-none">
		<li class="inline">
			<WorkTag tag={tree.node} fade={!tree.real} onclick={onClickTag} forTree={true} />
		</li>
		{#if tree.children?.length}
			{#each tree.children as t, i (i)}
				<li>
					{@render recur(t)}
				</li>
			{/each}
		{/if}
	</ul>
{/snippet}

{@render recur(tree)}

<style>
	ul > li > ul {
		&::before {
			content: '\21B3';
		}
		& > li > ul {
			margin-left: 0.5rem;
		}
	}
</style>
