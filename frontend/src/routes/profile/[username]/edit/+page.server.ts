import client from '$lib/api';
import { hasUserLevelOld } from '$lib/enums/UserLevel';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.user || params.username !== locals.user?.username)
		redirect(303, `/profile/${params.username}`);

	const [payloadConnections, payloadInvites] = await Promise.all([
		client.GET('/api/profile/connection', {
			fetch,
			params: {
				query: {
					username: params.username
				}
			}
		}),
		hasUserLevelOld(locals.user?.level, 'EDITOR')
			? client.GET('/api/auth/invites', {
					fetch
				})
			: Promise.resolve(null)
	]);

	return {
		user: locals.user,
		connections: payloadConnections.data,
		invites: payloadInvites?.data
			? {
					invites: payloadInvites.data[0],
					restrictedInvitee: payloadInvites.data[1]
				}
			: null
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
