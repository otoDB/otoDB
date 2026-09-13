import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { get_svg_gv, prepare_work_graph } from '$lib/viz.server';
import { asEnum, enumValues } from '$lib/enums';
import { WorkRelationTypes } from '$lib/schema';

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const {
		data: [relations, works]
	} = await client.GET('/api/work/relations', {
		params: {
			query: {
				work_id: params.work_id
			}
		},
		fetch
	});

	if (relations.length === 0) return;

	const direction_param = url.searchParams.get('rel_dir'),
		allowed_types_param = url.searchParams.getAll('rel_allowed_types'),
		show_thumbs_par = url.searchParams.get('rel_show_thumbs'),
		degree = parseInt(url.searchParams.get('rel_deg') ?? '0', 10) || 1;
	const allowed_types =
		allowed_types_param.length !== 0
			? (allowed_types_param
					.map((v) => asEnum(WorkRelationTypes, v))
					.filter((v) => v) as WorkRelationTypes[])
			: enumValues(WorkRelationTypes);
	const show_thumbs = show_thumbs_par === null || show_thumbs_par === 'true';

	const [nodes, links, images, max_distance, auto_dir] = prepare_work_graph(
		works,
		relations,
		params.work_id,
		allowed_types,
		degree,
		show_thumbs
	);
	const direction = (['LR', 'TB'] as unknown[]).includes(direction_param)
		? (direction_param as 'LR' | 'TB')
		: auto_dir;
	const svg = get_svg_gv(nodes, links, direction, show_thumbs ? images : undefined);

	return {
		works,
		svg,
		direction,
		allowed_types,
		degree,
		max_distance,
		show_thumbs
	};
};
