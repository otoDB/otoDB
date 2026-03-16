import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ fetch, params, locals }) => {
	if (isNaN(+params.list_id)) error(400, { message: 'Bad request' });

	const { data, error: e } = await client.GET('/api/list/list', {
		fetch,
		params: {
			query: {
				list_id: +params.list_id
			}
		}
	});
	if (e) error(404, { message: 'Not found' });

	return {
		list: data,
		links: [
			{
				pathname: `list/${params.list_id}`,
				title: m.stale_loose_squid_cut() + ' ' + params.list_id
			},
			...(locals.user && locals.user.user_id === data.author.id
				? [{ pathname: `list/${params.list_id}/edit`, title: m.minor_crisp_cobra_list() }]
				: [])
		],
		head: {
			title: data.name,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.stale_loose_squid_cut(), url: '/list/search' },
				{ name: data.name, url: `/list/${params.list_id}` }
			]
		}
	};
};
