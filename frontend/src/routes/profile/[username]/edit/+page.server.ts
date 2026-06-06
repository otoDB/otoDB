import client, { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { hasUserLevel } from '$lib/enums/userLevel';
import { redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Levels } from '$lib/schema';

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
		hasUserLevel(locals.user?.level, Levels.Editor)
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
		const { error } = await rawClient.PUT('/api/profile/connection', {
			fetch,
			params: { query: { urls } }
		});
		if (error) return apiFail(error);
		redirect(303, `/profile/${params.username}`);
	}
} satisfies Actions;
