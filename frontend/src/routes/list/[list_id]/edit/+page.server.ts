import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client from '$lib/api';

export const load: PageServerLoad = async ({ params, parent }) => {
	const data = await parent();
	if (!data.user || data.list?.author?.username !== data.user?.username)
		redirect(303, `/list/${params.list_id}`);
};

export const actions = {
	default: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const name = data.get('name') as string,
			description = data.get('description') as string;

		const { error, data: _list_id } = await client.PUT('/api/list/list', {
			fetch,
			params: { query: { list_id: +params.list_id! } },
			body: {
				name,
				description
			}
		});
		if (error) return fail(400, { name, description, failed: true });

		redirect(303, `/list/${params.list_id}`);
	}
} satisfies Actions;
