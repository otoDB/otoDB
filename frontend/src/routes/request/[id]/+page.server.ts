import client from '$lib/api';
import { error } from '@sveltejs/kit';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';
import { PathsApiCommentCommentsGetParametersQueryModel } from '$lib/schema';

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
					model: PathsApiCommentCommentsGetParametersQueryModel.bulkrequest,
					pk: +params.id
				}
			}
		})
	]);


	// TODO: Error forwarding
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
