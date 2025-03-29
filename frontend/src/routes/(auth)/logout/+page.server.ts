import client from '$lib/api';
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ request, cookies, fetch, locals }) => {
	if (!locals.user) redirect(303, '/');

	const { error } = await client.POST('/api/auth/logout', { fetch });

	if (!error) {
		cookies.delete('csrftoken', { path: '/' });
		cookies.delete('sessionid', { path: '/' });
	}

	redirect(303, '/');
};
