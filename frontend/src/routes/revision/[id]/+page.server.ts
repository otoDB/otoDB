import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { isValidEntityModelType, type EntityModelType } from '$lib/enums';
import type { components, Route } from '$lib/schema';

type RC = components['schemas']['RevisionChangeSchema'];
type Row = { target_type: string; tg_id: string; target_id: string; rcs: RC[] };
const group_RCs = (
	items: RC[]
): {
	route: Route;
	entities: { rows: Row[]; ent_type: EntityModelType; ent_id: string }[];
}[] =>
	(Object.values(Object.groupBy(items, (c) => c.route)) as RC[][])
		.map((rent) => ({
			route: rent![0].route,
			entities: (Object.values(Object.groupBy(rent!, (c) => c.ent_type + c.ent_id)) as RC[][])
				.map((cs) => cs.filter((c) => isValidEntityModelType(c.ent_type)))
				.filter((ec) => ec.length)
				.map((tg) => ({
					ent_type: tg[0].ent_type as EntityModelType,
					ent_id: tg[0].ent_id,
					rows: (
						Object.values(Object.groupBy(tg, (c) => c.target_type + ':' + c.target_id)) as RC[][]
					).map((rcs) => ({
						target_type: rcs[0].target_type,
						tg_id: rcs[0].tg_id,
						target_id: rcs[0].target_id,
						rcs
					}))
				}))
		}))
		.filter(({ entities }) => entities.length);

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const revision_id = params.id;

	const [{ data: revision }, { data: changes }] = await Promise.all([
		client.GET('/api/history/revision', {
			fetch,
			params: { query: { revision_id } }
		}),
		client.GET('/api/history/revision_changes', {
			fetch,
			params: {
				query: {
					revision_id
				}
			}
		})
	]);

	return {
		revision,
		changes,
		routes: group_RCs(changes.changes)
	};
};
