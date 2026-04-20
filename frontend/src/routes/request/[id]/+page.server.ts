import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import { ModelsWithComments } from '$lib/schema';
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
					model: ModelsWithComments.bulkrequest,
					pk: +params.id
				}
			}
		})
	]);

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
