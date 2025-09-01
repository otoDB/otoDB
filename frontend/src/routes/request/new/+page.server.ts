import client from '$lib/api';
import { fail, redirect, type Actions } from '@sveltejs/kit';

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const actions = data.get('actions') as string;
		const { data: r, error } = await client.POST('/api/request/new', {
			fetch,
			params: { query: { s: actions } }
		});
		if (error) fail(400);
		redirect(303, `/request/${r}`);
	}
} satisfies Actions;
