import client from '$lib/api';
import { error } from '@sveltejs/kit';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const paramId = parseInt(params.id, 10);

	const [{ data }, { data: comments }] = await Promise.all([
		client.GET('/api/request/request', {
			fetch,
			params: {
				query: {
					request_id: paramId
				}
			}
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: {
				query: {
					model: 'bulkrequest',
					pk: +params.id
				}
			}
		})
	]);

	if (!data) error(500, 'Failed to fetch data.');
	if (!comments) error(500, 'Failed to fetch data.');

	return {
		request: data,
		id: paramId,
		comments,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.last_jumpy_barbel_mop(),
				name: `#${paramId}`
			})
		}
	};
};
