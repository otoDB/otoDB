import client from '$lib/api';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { UserLevel } from '$lib/enums';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.user || params.username !== locals.user?.username)
		redirect(303, `/profile/${params.username}`);

	const [{ data }, { data: invites }] = await Promise.all([
		client.GET('/api/profile/connection', {
			fetch,
			params: {
				query: {
					username: params.username
				}
			}
		}),
		locals.user.level >= UserLevel.EDITOR
			? client.GET('/api/auth/invites', { fetch })
			: { data: [[], null] }
	]);

	return {
		connections: data,
		invites
	};
};

export const actions = {
	connections: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const urls = (data.get('urls') as string) ?? '';
		await client.PUT('/api/profile/connection', {
			fetch,
			params: { query: { urls } }
		});
		redirect(303, `/profile/${params.username}`);
	}
} satisfies Actions;
