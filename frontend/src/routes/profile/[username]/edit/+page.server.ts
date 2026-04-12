import client from '$lib/api';
import { hasUserLevel, resolveUserLevelById } from '$lib/enums/UserLevel';
import { error, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, locals }) => {
	if (!locals.user || params.username !== locals.user?.username)
		redirect(303, `/profile/${params.username}`);

	const { data: dataConnections, error: errorConnection } = await client.GET(
		'/api/profile/connection',
		{
			fetch,
			params: {
				query: {
					username: params.username
				}
			}
		}
	);
	if (errorConnection) error(500, 'Failed to load profile connections');
	if (!dataConnections) error(500, 'Failed to load profile connections');

	if (hasUserLevel(resolveUserLevelById(locals.user.level), 'EDITOR')) {
		const { data: invitesData, error: errorInvites } = await client.GET('/api/auth/invites', {
			fetch
		});
		if (errorInvites) error(500, 'Failed to load invites');
		if (!invitesData) error(500, 'Failed to load invites');

		const [invites, restrictedInvitee] = invitesData;

		return {
			user: locals.user,
			connections: dataConnections,
			invites: {
				invites,
				restrictedInvitee: restrictedInvitee
			}
		};
	} else {
		return {
			user: locals.user,
			connections: dataConnections,
			invites: null
		};
	}　
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
