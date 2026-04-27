import client from '$lib/api.server';
import type { PageServerLoad } from './$types';
import { isValidEntityModelType, type EntityModelType } from '$lib/enums';
import type { components, Route } from '$lib/schema';

type RC = components['schemas']['RevisionChangeSchema'];
const group_RCs = (
	items: RC[]
): { route: Route; entities: { rcs: RC[]; ent_type: EntityModelType; ent_id: string }[] }[] =>
	(Object.values(Object.groupBy(items, (c) => c.route)) as RC[][])
		.map((rent) => ({
			route: rent![0].route,
			entities: (Object.values(Object.groupBy(rent!, (c) => c.ent_type + c.ent_id)) as RC[][])
				.map((cs) => cs.filter((c) => isValidEntityModelType(c.ent_type)))
				.filter((ec) => ec.length)
				.map((tg) => ({
					ent_type: tg[0].ent_type as EntityModelType,
					ent_id: tg[0].ent_id,
					rcs: tg
				}))
		}))
		.filter(({ entities }) => entities.length);

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const revision_id = params.id;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const batch_size = 30;

	const [{ data: revision }, { data: changes }] = await Promise.all([
		client.GET('/api/history/revision', {
			fetch,
			params: { query: { revision_id } }
		}),
		client.GET('/api/history/revision_changes', {
			fetch,
			params: {
				query: {
					revision_id,
					limit: batch_size,
					offset: batch_size * (page - 1)
				}
			}
		})
	]);

	return {
		revision,
		changes,
		page,
		batch_size,
		routes: group_RCs(changes.items)
	};
};
