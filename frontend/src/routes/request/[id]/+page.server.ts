import client from '$lib/api';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const [{ data }, { data: comments }] = await Promise.all([
		client.GET('/api/request/request', {
			fetch,
			params: {
				query: {
					request_id: +params.id
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

	return {
		request: data,
		...params,
		comments,
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.last_jumpy_barbel_mop(),
				name: '#' + params.id
			})
		}
	};
};
