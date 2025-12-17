import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ fetch, params, locals, url }) => {
	if (isNaN(+params.list_id)) error(400, { message: 'Bad request' });

	const batch_size = 20;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;

	const { data, error: e } = await client.GET('/api/list/list', {
		fetch,
		params: {
			query: {
				list_id: +params.list_id
			}
		}
	});
	if (e) error(404, { message: 'Not found' });

	const { data: entries } = await client.GET('/api/list/entries', {
		fetch,
		params: {
			query: {
				list_id: +params.list_id,
				limit: batch_size,
				offset: (page - 1) * batch_size
			}
		}
	});
	return {
		batch_size,
		page,
		list: data,
		entries,
		links: [
			{
				pathname: `list/${params.list_id}`,
				title: m.stale_loose_squid_cut() + ' ' + params.list_id
			},
			...(locals.user && locals.user.user_id === data.author.id
				? [{ pathname: `list/${params.list_id}/edit`, title: m.minor_crisp_cobra_list() }]
				: [])
		]
	};
};
