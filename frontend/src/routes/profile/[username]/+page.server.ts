import client, { commentClient } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, parent, params }) => {
	const data = await parent();
	const comments = await commentClient.GET('account', data.profile.id, fetch);

	const { data: connections } = await client.GET('/api/profile/connection', {
		fetch,
		params: {
			query: {
				username: params.username
			}
		}
	});

	return { comments, connections };
};
