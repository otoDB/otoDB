import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { type EntityModelType } from '$lib/enums';

export const _buildRoutes = (
	items: {
		target_type: string;
		ent_type: string;
		ent_id: string;
		route: number;
		tg_id: string;
		deleted: boolean;
		target_column?: string | null;
		target_value?: string | null;
	}[]
) => {
	return (
		Object.values(Object.groupBy(items, (c) => c.route)).map((rent) => [
			rent![0].route,
			Object.values(Object.groupBy(rent!, (c) => c.ent_type + c.ent_id))
				.filter((ec) => ec!.length)
				.map((tg) => [[tg![0].ent_type, tg![0].ent_id], tg])
		]) as [
			number,
			[
				[EntityModelType, string],
				{
					target_type: string;
					ent_type: string;
					ent_id: string;
					route: number;
					tg_id: string;
					deleted: boolean;
					target_column: string;
					target_value?: string | null;
				}[]
			][]
		][]
	).filter((rc) => rc[1].length > 0);
};

export const load: PageServerLoad = async ({ params, fetch, url }) => {
	const revision_id = +params.id;
	if (isNaN(revision_id)) error(400, { message: 'Bad request' });
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const batch_size = 30;

	const [{ data: changes }, { data: revision }] = await Promise.all([
		client.GET('/api/history/revision_changes', {
			fetch,
			params: {
				query: {
					revision_id,
					limit: batch_size,
					offset: batch_size * (page - 1)
				}
			}
		}),
		client.GET('/api/history/revision', { fetch, params: { query: { revision_id } } })
	]);

	if (!revision) error(404, { message: 'Not found' });

	if (!changes) error(500, { message: 'Internal server error' });
	if (!revision) error(500, { message: 'Internal server error' });

	return {
		revision,
		changes,
		page,
		batch_size,
		routes: _buildRoutes(changes.items)
	};
};
