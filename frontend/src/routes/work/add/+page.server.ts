import { error, fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';

const next_redirect = (user: App.Locals['user']) => {};

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const link = url.searchParams.get('url');
	if (link) {
		const { error: err } = await client.POST('/api/work/source', {
			fetch,
			params: { query: { url: link, is_reupload: false } }
		});
		if (err) error(400, err);
		else next_redirect(locals.user);
	}

	const work = url.searchParams.get('for_work');
	if (work && !isNaN(+work)) {
		const { data, error: e } = await client.GET('/api/work/work', {
			params: {
				query: {
					work_id: +work
				}
			},
			fetch
		});
		if (e) error(404, { message: 'Not found' });

		return {
			title: data.title
		};
	}
};

export const actions = {
	default: async ({ request, fetch, url, locals }) => {
		const data = await request.formData();
		const link = data.get('url') as string,
			is_official = !!data.get('origin');
		const work = url.searchParams.get('for_work');

		const { data: source_id, error } = await client.POST('/api/work/source', {
			fetch,
			params: {
				query: { url: link, is_reupload: !is_official, work_id: work ? +work : null }
			}
		});
		if (error) return fail(400, { url: link, origin: is_official, failed: true });

		if (work && !isNaN(+work)) redirect(303, `/work/${+work}`);
		else {
			// new work
			if (locals.user.level >= UserLevel.MODERATOR) {
				const { data: new_work, error: e } = await client.POST('/api/work/assign_source', {
					fetch,
					params: { query: { source_id } }
				});
				if (e) redirect(303, '/work/unbound');
				else redirect(303, `/work/${new_work}`);
			} else redirect(303, `/profile/${locals.user.username}/submissions`);
		}
	}
} satisfies Actions;
