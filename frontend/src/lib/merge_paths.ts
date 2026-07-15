import type { ComponentProps } from 'svelte';
import { SvelteMap } from 'svelte/reactivity';
import type WorkTagTree from '$lib/WorkTagTree.svelte';

type TreeNode = ComponentProps<typeof WorkTagTree>['tree']['node'];

export const merge_paths = <T extends TreeNode & { primary_path: TreeNode[] }>(
	paths: T[]
): ComponentProps<typeof WorkTagTree>['tree'][] => {
	const graph: SvelteMap<string, Set<string>> = new SvelteMap();
	paths
		.filter((p) => p.primary_path.length)
		.forEach((path) =>
			path.primary_path.forEach((p, i, a) => {
				const next_node = (i + 1 === a.length ? path : a[i + 1]).slug;
				if (graph.has(p.slug)) graph.get(p.slug)?.add(next_node);
				else graph.set(p.slug, new Set([next_node]));
			})
		);
	const traverse = (node: string): ComponentProps<typeof WorkTagTree>['tree'] => ({
		node: [...paths, ...paths.flatMap((p) => p.primary_path)].find((n) => n.slug === node)!,
		real: paths.some((n) => n.slug === node),
		children: Array.from(graph.get(node) ?? []).map((n) => traverse(n))
	});
	return [
		...graph
			.keys()
			.filter((n) => !graph.values().some((s) => s.has(n)))
			.map(traverse),
		...paths
			.filter((p) => p.primary_path.length === 0 && !graph.has(p.slug))
			.map((n) => ({ node: n, real: true }))
	];
};
