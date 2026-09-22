import { SongRelationTypes, WorkRelationTypes, type components } from '$lib/schema';
import { getDisplayText } from '$lib/ui';
import * as Viz from '@viz-js/viz';
import { SongRelationNames, WorkRelationNames } from '$lib/enums';
import { m } from './paraglide/messages.js';
type Work = Omit<components['schemas']['SlimWorkSchema'], 'status'>;
type Song = components['schemas']['SlimSongSchema'];
type Node<T> = (T extends 'work' ? Work : Song) & { distance?: number };
type RelationType<T> = T extends 'work' ? WorkRelationTypes : SongRelationTypes;
type Edge<T> = { A_id: string; B_id: string; relation: RelationType<T> };

const relation_BFS = <T>(
	ns: Node<T>[],
	ls: Edge<T>[],
	start: string,
	allowed_types: RelationType<T>[],
	max_distance: number = Number.POSITIVE_INFINITY
): [(Node<T> & { distance: number })[], Edge<T>[], string[]] => {
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
							.filter((v) => allowed_types.includes(v.relation) && (v.A_id === n || v.B_id === n))
							.flatMap((v) => [v.A_id, v.B_id])
					)
				].map((nn) => [nn, curr_distance + 1] as [string, number])
			);
		}
		queue = next_queue;
	}
	return [
		nodes.filter((v) => v.distance !== undefined) as (Node<T> & { distance: number })[],
		links.filter(
			(v) =>
				allowed_types.includes(v.relation) &&
				nodes.find((w) => w.id === v.A_id)?.distance !== undefined &&
				nodes.find((w) => w.id === v.B_id)?.distance !== undefined
		),
		[
			...new Set(
				links
					.filter((v) => allowed_types.includes(v.relation))
					.map((v) => [v.A_id, v.B_id].map((n) => nodes.find((w) => w.id === n)!))
					.filter(([a, b]) => (a.distance === undefined) !== (b.distance === undefined))
					.map(([a, b]) => (a.distance !== undefined ? a.id : '-' + b.id))
			)
		]
	];
};
const gv_font = 'Arial';
// A node and each of its edges share a rel_<id> class, which is how hovering one finds the other
const rel_class = (...ids: string[]) => ids.map((i) => `rel_${i}`).join(' ');
const image_url = (u: string | null | undefined) => (u && URL.parse(u)?.href) || null;
const gv_node = <T>(id: string, ob: Node<T>, url: string, show_thumbs: boolean) => {
	const thumb = show_thumbs ? image_url((ob as Work).thumbnail) : null;
	return {
		name: ob.id,
		attributes: {
			label: getDisplayText(ob.title),
			tooltip: getDisplayText(ob.title),
			URL: url,
			class: `${rel_class(ob.id)}${ob.title === null ? ' untitled' : ''}${thumb ? ' thumb' : ''}`,
			...(ob.id === id ? { id: 'graph_current' } : {}),
			...(thumb ? { image: thumb, imagescale: 'true', imagepos: 'tc', labelloc: 'b' } : {})
		}
	};
};
const gv_more_node = (a: string) => ({
	name: `more:${a}`,
	attributes: {
		label: m.fresh_deft_warbler_edit(),
		tooltip: m.fresh_deft_warbler_edit(),
		shape: 'plaintext'
	}
});
const gv_more_edge = (a: string) => {
	const attributes = { style: 'dashed', dir: 'none', tooltip: m.fresh_deft_warbler_edit() };
	return a[0] === '-'
		? { tail: a.slice(1), head: `more:${a}`, attributes }
		: { tail: `more:${a}`, head: a, attributes };
};

const auto_dir = (links: { A_id: string; B_id: string }[]) => {
	// heuristic from VNDB's `gen_dot`
	const fanout: Record<string, number> = {};
	for (const l of links) {
		fanout[l.A_id] = (fanout[l.A_id] ?? 0) + 1;
		fanout[l.B_id] = (fanout[l.B_id] ?? 0) + 1;
	}
	return Math.max(0, ...Object.values(fanout)) > 6 ? 'LR' : 'TB';
};

export const prepare_work_graph = (
	objects: Work[],
	relations: Edge<'work'>[],
	id: string,
	allowed_types: WorkRelationTypes[],
	distance: number,
	show_thumbs: boolean
): [Viz.Node[], Viz.Edge[], Viz.ImageSize[], number, 'TB' | 'LR'] => {
	const [nodes, links, ext] = relation_BFS<'work'>(objects, relations, id, allowed_types, distance);
	return [
		[
			...nodes.map((ob) => gv_node<'work'>(id, ob, `/work/${ob.id}`, show_thumbs)),
			...ext.map(gv_more_node)
		],
		[
			...links.map((r) => {
				const [tail, head] =
					r.relation === WorkRelationTypes.Sequel ? [r.B_id, r.A_id] : [r.A_id, r.B_id];
				const label = WorkRelationNames[r.relation]();
				return {
					tail,
					head,
					attributes: { label, tooltip: label, class: rel_class(tail, head) }
				};
			}),
			...ext.map(gv_more_edge)
		],
		nodes.flatMap((ob) => {
			const name = image_url(ob.thumbnail);
			return name ? [{ name, width: 160, height: 120 }] : [];
		}),
		Math.max(...relation_BFS(objects, relations, id, allowed_types)[0].map((n) => n.distance)),
		auto_dir(links)
	];
};

export const prepare_song_graph = (
	objects: Song[],
	relations: Edge<'song'>[],
	id: string,
	allowed_types: SongRelationTypes[],
	distance: number
): [Viz.Node[], Viz.Edge[], number] => {
	const [nodes, links, ext] = relation_BFS<'song'>(objects, relations, id, allowed_types, distance);
	return [
		[
			...nodes.map((ob) => gv_node<'song'>(id, ob, `/tag/${ob.work_tag}`, false)),
			...ext.map(gv_more_node)
		],
		[
			...links.map((r) => {
				const label = SongRelationNames[r.relation]();
				return {
					tail: r.A_id,
					head: r.B_id,
					attributes: { label, tooltip: label, class: rel_class(r.A_id, r.B_id) }
				};
			}),
			...ext.map(gv_more_edge)
		],
		Math.max(...relation_BFS(objects, relations, id, allowed_types)[0].map((n) => n.distance))
	];
};

const viz = await Viz.instance();
export const get_svg_gv = (
	nodes: Viz.Node[],
	edges: Viz.Edge[],
	direction: 'TB' | 'LR',
	images?: Viz.ImageSize[]
) => {
	return viz.renderString(
		{
			nodes,
			edges,
			nodeAttributes: { shape: 'box', fontname: gv_font, fontsize: 9 },
			edgeAttributes: { minlen: 2, fontname: gv_font, fontsize: 8, arrowsize: 0.7 }
		},
		{
			format: 'svg_inline',
			graphAttributes: { bgcolor: 'transparent', rankdir: direction },
			images
		}
	);
};
