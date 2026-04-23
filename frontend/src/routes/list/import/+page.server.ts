import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { Levels } from '$lib/schema';

export const load: PageServerLoad = async ({ locals, url }) => {
	userLevelGuard(locals.user, Levels.Editor, url.pathname);
	return { head: { title: m.proof_heroic_rat_cuddle() } };
};

export const actions = {
	default: async ({ request, fetch }) => {
		const data = await request.formData();
		const link = data.get('url') as string;

		let list_id: number | null = null;
		try {
			({ data: list_id } = await client.POST('/api/list/import', {
				fetch,
				params: { query: { url: link } }
			}));
		} catch {
			return fail(400, { url: link, failed: true });
		}
		redirect(303, `/list/${list_id}`);
	}
} satisfies Actions;
