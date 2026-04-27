import client from '$lib/api.server';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { userLevelGuard } from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Member);
	const preFilledData = url.searchParams.get('pre_filled');
	return { preFilledData, head: { title: m.muddy_tough_swan_view() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const actions = data.get('actions') as string;
		let request_id: null | string = null;
		try {
			({ data: request_id } = await client.POST('/api/request/new', {
				fetch,
				params: { query: { s: actions } }
			}));
		} catch {
			return fail(400);
		}
		redirect(303, `/request/${request_id}`);
	}
} satisfies Actions;
