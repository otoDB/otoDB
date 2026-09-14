import client from '$lib/api.server';
import { ModelsWithComments, SongRelationTypes } from '$lib/schema';
import { prepare_song_graph, get_svg_gv } from '$lib/viz.server';
import { asEnum, enumValues } from '$lib/enums';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent, url }) => {
	const data = await parent();

	const batch_size = 20;

	const [
		{ data: details },
		{ data: works },
		{ data: connections },
		{ data: comments },
		{ data: similar }
	] = await Promise.all([
		client.GET('/api/tag/details', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/tag/works', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug,
					limit: batch_size,
					offset: 0
				}
			}
		}),
		client.GET('/api/tag/connection', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: {
				query: {
					model: ModelsWithComments.tagwork,
					pk: data.tag.id
				}
			}
		}),
		client.GET('/api/tag/similar', {
			fetch,
			params: { query: { tag_slug: params.tag_slug } }
		})
	]);

	const r = {
		...details,
		works,
		comments,
		batch_size,
		connections,
		similar
	};

	if (data.tag.song) {
		const [
			{ data: song_connections },
			{
				data: [relations, songs]
			}
		] = await Promise.all([
			client.GET('/api/tag/song_connection', {
				fetch,
				params: { query: { song_id: data.tag.song.id } }
			}),
			client.GET('/api/tag/song_relations', {
				fetch,
				params: {
					query: {
						song_id: data.tag.song.id
					}
				}
			})
		]);

		if (relations.length === 0) return { ...r, song_connections };

		const direction_param = url.searchParams.get('rel_dir'),
			allowed_types_param = url.searchParams.getAll('rel_allowed_types'),
			degree = Math.max(1, parseInt(url.searchParams.get('rel_deg') ?? '0', 10) || 1);
		const allowed_types =
			allowed_types_param.length !== 0
				? allowed_types_param
						.map((v) => asEnum(SongRelationTypes, Number(v)))
						.filter((v): v is SongRelationTypes => v !== null)
				: enumValues(SongRelationTypes);
		const direction = (['LR', 'TB'] as unknown[]).includes(direction_param)
			? (direction_param as 'LR' | 'TB')
			: 'LR';

		const [nodes, links, max_distance] = prepare_song_graph(
			songs,
			relations,
			data.tag.song.id,
			allowed_types,
			degree
		);
		const svg = get_svg_gv(nodes, links, direction);
		return { ...r, song_connections, svg, direction, allowed_types, degree, max_distance };
	} else return r;
};
