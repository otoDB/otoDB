import { rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { redirect, type Actions } from '@sveltejs/kit';
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
		const { data: request_id, error: apiError } = await rawClient.POST('/api/request/new', {
			fetch,
			params: { query: { s: actions } }
		});
		if (apiError) return apiFail(apiError);
		redirect(303, `/request/${request_id}`);
	}
} satisfies Actions;
