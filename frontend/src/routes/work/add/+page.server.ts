import { error, fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client from '$lib/api';
import { UserLevel } from '$lib/enums';
import userLevelGuard from '$lib/route_guard';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
	userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);

	const link = url.searchParams.get('url');
	const work = url.searchParams.get('for_work');
	const isNewWork = work === null;
	let title = null;
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
		title = data.title;
	}
	return {
		title,
		link,
		isNewWork
	};
};

export const actions = {
	default: async ({ request, fetch, url, locals }) => {
		const data = await request.formData();
		const link = data.get('url') as string,
			is_official = data.get('origin') === 'true',
			original_url = data.get('original_url'),
			rating = data.get('rating');
		const work = url.searchParams.get('for_work');

		// Build metadata object
		const allow_dead = data.get('allow_dead') === 'on';
		const metadata = {
			allow_dead,
			is_reupload: !is_official,
			title: (data.get('manual_title') as string) || null,
			description: (data.get('manual_description') as string) || null,
			uploader_id: (data.get('manual_uploader_id') as string) || null,
			thumbnail_url: (data.get('manual_thumbnail_url') as string) || null,
			work_width: data.get('manual_width') ? +(data.get('manual_width') as string) : null,
			work_height: data.get('manual_height') ? +(data.get('manual_height') as string) : null,
			work_duration: data.get('manual_duration') ? +(data.get('manual_duration') as string) : null,
			published_date: (data.get('manual_date') as string) || null
		};

		const {
			data: work_id,
			error,
			response
		} = await client.POST('/api/work/source', {
			fetch,
			params: {
				query: {
					url: link,
					work_id: work ? +work : undefined,
					rating: rating ? +rating : undefined,
					original_url: (original_url as string) || undefined
				}
			},
			body: metadata
		});

		if (response.status === 409) {
			return fail(409, {
				url: link,
				origin: is_official,
				failed: true,
				message: m.sour_loud_baboon_dance()
			});
		}
		if (error)
			return fail(400, {
				url: link,
				origin: is_official,
				failed: true,
				message: m.careful_lost_jaguar_dart()
			});

		// New source to existing work flow
		if (work && !isNaN(+work)) redirect(303, `/work/${+work}`);

		// New source to new work flow
		if (work_id) redirect(303, `/work/${work_id}/tags`);
		else redirect(303, `/profile/${locals.user.username}/submissions`);
	}
} satisfies Actions;
