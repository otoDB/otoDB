import { enumValues, SongRelationNames, WorkRelationNames } from '$lib/enums';
import { m } from '$lib/paraglide/messages.js';
import {
	GraphViewBackends,
	SongRelationTypes,
	WorkRelationTypes,
	type components
} from '$lib/schema';
import { getDisplayText } from '$lib/ui';
import * as Viz from '@viz-js/viz';

export type GraphType = 'work' | 'song';
export type Direction = 'TB' | 'LR';

type Work = Omit<components['schemas']['SlimWorkSchema'], 'status'>;
type Song = components['schemas']['SongSchema'];
type GraphNode = (Work | Song) & { distance?: number };
type PlacedNode = GraphNode & { distance: number };
type GraphEdge = { A_id: string; B_id: string; relation: number };

export type RelationData = [GraphEdge[], GraphNode[]];

export interface GraphOptions {
	type: GraphType;
	id: string;
	deg: number;
	dir: Direction | null;
	thumbs: boolean;
	types: number[] | null;
	backend: GraphViewBackends;
}

export interface GraphView {
	empty: boolean;
	deg: number;
	max_distance: number;
	dir: Direction;
	svg: string | null;
	mermaid: string | null;
}

const relationTypes = (type: GraphType) =>
	enumValues(type === 'work' ? WorkRelationTypes : SongRelationTypes) as number[];

const relationNames = (type: GraphType) =>
	(type === 'work' ? WorkRelationNames : SongRelationNames) as Record<number, () => string>;

const nodeURL = (type: GraphType, node: GraphNode) =>
	type === 'work' ? `/work/${node.id}` : `/tag/${(node as Song).work_tag}`;

const relation_BFS = (
	ns: GraphNode[],
	ls: GraphEdge[],
	allowed: ReadonlySet<number>,
	start: string,
	max_distance: number = Number.POSITIVE_INFINITY
): [PlacedNode[], GraphEdge[], string[]] => {
	const nodes = structuredClone(ns),
		links = structuredClone(ls);
	let queue: [string, number][] = [[start, 0]];
	while (queue.length) {
		const next_queue: [string, number][] = [];
		for (const [n, curr_distance] of queue) {
			const ng = nodes.find((nn) => nn.id === n)!;
			if (curr_distance > max_distance || ng.distance !== undefined) continue;
			ng.distance = curr_distance;
			next_queue.push(
				...[
					...new Set(
						links
							.filter((v) => allowed.has(v.relation) && (v.A_id === n || v.B_id === n))
							.flatMap((v) => [v.A_id, v.B_id])
					)
				].map((nn) => [nn, curr_distance + 1] as [string, number])
			);
		}
		queue = next_queue;
	}
	return [
		nodes.filter((v) => v.distance !== undefined) as PlacedNode[],
		links.filter(
			(v) =>
				allowed.has(v.relation) &&
				nodes.find((w) => w.id === v.A_id)?.distance !== undefined &&
				nodes.find((w) => w.id === v.B_id)?.distance !== undefined
		),
		[
			...new Set(
				links
					.filter((v) => allowed.has(v.relation))
					.map((v) => [v.A_id, v.B_id].map((n) => nodes.find((w) => w.id === n)!))
					.filter(([a, b]) => (a.distance === undefined) !== (b.distance === undefined))
					.map(([a, b]) => (a.distance !== undefined ? a.id : '-' + b.id))
			)
		]
	];
};

export const asDirection = (value: unknown): Direction | null =>
	value === 'LR' || value === 'TB' ? value : null;

// heuristic from VNDB's `gen_dot`
const auto_dir = (links: GraphEdge[]): Direction => {
	const fanout: Record<string, number> = {};
	for (const l of links) {
		fanout[l.A_id] = (fanout[l.A_id] ?? 0) + 1;
		fanout[l.B_id] = (fanout[l.B_id] ?? 0) + 1;
	}
	return Math.max(0, ...Object.values(fanout)) > 6 ? 'LR' : 'TB';
};

// Relations of this type read backwards, so the arrow is drawn the other way round
const reversed = (type: GraphType, relation: number) =>
	type === 'work' && relation === WorkRelationTypes.Sequel;

const mermaid_source = (
	{ type, id, thumbs }: GraphOptions,
	dir: Direction,
	nodes: PlacedNode[],
	links: GraphEdge[],
	ext: string[]
) => {
	const names = relationNames(type);
	const thumb = (node: GraphNode) =>
		type === 'work' && thumbs ? ((node as Work).thumbnail ?? null) : null;
	const label = (node: GraphNode) =>
		`${node.id}["${getDisplayText(node.title).replaceAll('"', '#quot;')}"]${
			node.title === null ? ':::untitled' : ''
		}`;

	return [
		'---',
		'config:',
		'  layout: elk',
		'  elk:',
		'    mergeEdges: true',
		'---',
		`flowchart ${dir}`,
		`    style ${id} color:#f00`,
		'    classDef moreNodes fill:none,stroke:none;',
		'    classDef untitled font-style:italic;',
		...nodes.flatMap((node) => [
			...(type === 'work'
				? [
						`    ${node.id}@{ ${thumb(node) ? `img: "${thumb(node)}",` : ''} constraint: on, w: 10 }`
					]
				: []),
			`    ${label(node)}`,
			`    click ${node.id} "${nodeURL(type, node)}"`
		]),
		...links.map((r) => {
			const [tail, head] = reversed(type, r.relation) ? [r.B_id, r.A_id] : [r.A_id, r.B_id];
			// The `_tail_head_` id is what the hover highlighting looks edges up by
			return `    ${tail} _${tail}_${head}_@-->|${names[r.relation]()}| ${head}`;
		}),
		...ext.flatMap((a) => [
			`    ${a}MORE["${m.fresh_deft_warbler_edit()}"]`,
			`    class ${a}MORE moreNodes;`,
			a[0] !== '-' ? `    ${a}MORE -.- ${a}` : `    ${a.slice(1)} -.- ${a}MORE`
		])
	].join('\n');
};

const gv_font = 'Arial';
// A node and each of its edges share a rel_<id> class, which is how hovering one finds the other
const rel_class = (...ids: string[]) => ids.map((i) => `rel_${i}`).join(' ');

let instance: ReturnType<typeof Viz.instance> | null = null;
const viz = () => (instance ??= Viz.instance());

const graphviz_svg = async (
	{ type, id, thumbs }: GraphOptions,
	dir: Direction,
	nodes: PlacedNode[],
	links: GraphEdge[],
	ext: string[]
) => {
	const names = relationNames(type);
	const thumb = (node: GraphNode) =>
		type === 'work' && thumbs ? ((node as Work).thumbnail ?? null) : null;

	const graph = {
		nodes: [
			...nodes.map((node) => {
				const image = thumb(node);
				return {
					name: node.id,
					attributes: {
						label: getDisplayText(node.title),
						tooltip: getDisplayText(node.title),
						URL: nodeURL(type, node),
						class: `${rel_class(node.id)}${node.title === null ? ' untitled' : ''}${image ? ' thumb' : ''}`,
						...(node.id === id ? { id: 'graph_current' } : {}),
						...(image ? { image, imagescale: 'true', imagepos: 'tc', labelloc: 'b' } : {})
					}
				};
			}),
			...ext.map((a) => ({
				name: `more:${a}`,
				attributes: { label: m.fresh_deft_warbler_edit(), shape: 'plaintext' }
			}))
		],
		edges: [
			...links.map((r) => {
				const [tail, head] = reversed(type, r.relation) ? [r.B_id, r.A_id] : [r.A_id, r.B_id];
				return {
					tail,
					head,
					attributes: { label: names[r.relation](), class: rel_class(tail, head) }
				};
			}),
			...ext.map((a) =>
				a[0] === '-'
					? { tail: a.slice(1), head: `more:${a}`, attributes: { style: 'dashed', dir: 'none' } }
					: { tail: `more:${a}`, head: a, attributes: { style: 'dashed', dir: 'none' } }
			)
		]
	};

	try {
		return (await viz()).renderString(
			{
				...graph,
				nodeAttributes: { shape: 'box', fontname: gv_font, fontsize: 9 },
				edgeAttributes: { minlen: 2, fontname: gv_font, fontsize: 8, arrowsize: 0.7 }
			},
			{
				format: 'svg_inline',
				graphAttributes: { bgcolor: 'transparent', rankdir: dir },
				images: nodes
					.filter((node) => thumb(node))
					.map((node) => ({ name: thumb(node)!, width: 160, height: 120 }))
			}
		);
	} catch (e) {
		instance = null;
		throw e;
	}
};

export const buildGraphView = async (
	options: GraphOptions,
	[relations, objects]: RelationData
): Promise<GraphView> => {
	// The search starts from the centre, so without it there is nothing to walk
	if (!relations.length || !objects.some((o) => o.id === options.id))
		return { empty: true, deg: 1, max_distance: 0, dir: 'TB', svg: null, mermaid: null };

	const { types } = options;
	const allowed = new Set(
		Array.isArray(types)
			? relationTypes(options.type).filter((t) => types.includes(t))
			: relationTypes(options.type)
	);

	const reachable = relation_BFS(objects, relations, allowed, options.id)[0];
	const max_distance = Math.max(0, ...reachable.map((n) => n.distance));
	const deg = Math.max(Math.min(Math.trunc(Number(options.deg)) || 1, max_distance), 1);

	const [nodes, links, ext] = relation_BFS(objects, relations, allowed, options.id, deg);
	const dir = asDirection(options.dir) ?? auto_dir(links);

	const mermaid = options.backend === GraphViewBackends.Mermaid;

	return {
		empty: false,
		deg,
		max_distance,
		dir,
		svg: mermaid ? null : await graphviz_svg(options, dir, nodes, links, ext),
		mermaid: mermaid ? mermaid_source(options, dir, nodes, links, ext) : null
	};
};
