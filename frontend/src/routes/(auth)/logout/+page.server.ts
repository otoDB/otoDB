import { rawClient } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ cookies, fetch, locals }) => {
		if (!locals.user) redirect(303, '/');

		const { error } = await rawClient.POST('/api/auth/logout', { fetch });

		if (!error) {
			cookies.delete('csrftoken', { path: '/' });
			cookies.delete('sessionid', { path: '/' });
		}

		redirect(303, '/');
	}
};
