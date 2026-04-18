import client from '$lib/api';
import { hasUserLevel } from '$lib/enums/userLevel';
import { error, redirect, type Actions } from '@sveltejs/kit';
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

	if (payloadConnections.error) error(500, 'Failed to load profile connections');
	if (!payloadConnections.data) error(500, 'Failed to load profile connections');

	if (payloadInvites?.error) error(500, 'Failed to load invites');

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
