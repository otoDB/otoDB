import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, locals, url, parent }) => {
	if (!locals.user || params.username !== locals.user?.username)
		redirect(303, `/profile/${params.username}`);

	const { data } = await client.GET('/api/profile/connection', {
		fetch,
		params: {
			query: {
				username: params.username
			}
		}
	});

	return {
		connections: data
	};
};
