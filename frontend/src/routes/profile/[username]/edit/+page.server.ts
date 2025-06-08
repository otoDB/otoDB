import client from '$lib/api';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { ProfileConnectionParsers } from '$lib/enums';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
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

export const actions = {
	connections: async ({ request, fetch, params }) => {
		const data = await request.formData();
		const urls = (data.get('urls') as string) ?? '';
		const connections = [...new Set(urls.split('\n'))]
			.filter((x) => x.trim() !== '')
			.map(
				(url) =>
					ProfileConnectionParsers.map((p, i) => ({ site: i, content_id: p(url) }))
						.filter((v) => !!v.content_id)
						.at(-1) // !!! Attention here
			)
			.filter((v) => !!v);
		await client.PUT('/api/profile/connection', {
			body: connections,
			params: { query: { username: params.username! } }
		});
		redirect(303, `/profile/${params.username}`);
	}
} satisfies Actions;
