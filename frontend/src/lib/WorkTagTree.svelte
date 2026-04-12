<script lang="ts">
	import type { ComponentProps, Snippet } from 'svelte';
	import WorkTag from './WorkTag.svelte';

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

{#snippet recur(this_snippet: Snippet<[Snippet<any>, Tree]>, tree: Tree)}
	<ul class="my-0.5 list-none">
		<li class="inline">
			<WorkTag tag={tree.node} fade={!tree.real} onclick={onClickTag} forTree={true} />
		</li>
		{#if tree.children?.length}
			{#each tree.children as t, i (i)}
				<li>
					{@render this_snippet(this_snippet, t)}
				</li>
			{/each}
		{/if}
	</ul>
{/snippet}

{@render recur(recur, tree)}

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
