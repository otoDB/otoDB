import client, { rawClient } from '$lib/api.server';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages';
import { userLevelGuard } from '$lib/route_guard';
import { Levels, WorkStatus, type components } from '$lib/schema';
import { getDisplayText } from '$lib/ui';
import { error, fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url, locals }) => {
	userLevelGuard(locals.user, Levels.Member, url.pathname);

	const link = url.searchParams.get('url');
	const work = url.searchParams.get('for_work');
	const source = url.searchParams.get('for_source');

	let title = null;
	let unavailable_source = null;
	if (work) {
		const { data } = await client.GET('/api/work/work', {
			params: {
				query: {
					work_id: work
				}
			},
			fetch
		});
		title = data.title;
	} else if (source) {
		const { data } = await client.GET('/api/upload/source', {
			params: {
				query: {
					source_id: source
				}
			},
			fetch
		});
		if (data.work_status === WorkStatus.Available) error(400, { message: 'Bad Request' });
		unavailable_source = data;
		title = unavailable_source.title;
	}
	return {
		title,
		link,
		unavailable_source,
		head: {
			title: title
				? m.mild_loud_shad_enchant({
						type: unavailable_source
							? m.new_aloof_camel_read()
							: m.helpful_away_jay_succeed(),
						name: getDisplayText(title)
					})
				: m.helpful_away_jay_succeed()
		}
	};
};

export const actions = {
	default: async ({ request, fetch, url, locals }) => {
		const data = await request.formData();
		const link = data.get('url') as string,
			is_official = data.get('origin') === 'true';
		const work = url.searchParams.get('for_work');
		const source = url.searchParams.get('for_source');
		const editing_unavailable_source = !!source;

		// Build metadata object only if user is editor AND manual fields provided
		let metadata: components['schemas']['WorkSourceMetadataSchema'] | undefined = undefined;
		if (hasUserLevel(locals.user?.level, Levels.Editor)) {
			const hasManualData =
				data.get('manual_title') ||
				data.get('manual_description') ||
				data.get('manual_uploader_id') ||
				data.get('manual_thumbnail_url') ||
				data.get('manual_width') ||
				data.get('manual_height') ||
				data.get('manual_duration') ||
				data.get('manual_date');

			if (hasManualData) {
				metadata = {
					title: (data.get('manual_title') as string) || null,
					description: (data.get('manual_description') as string) || null,
					uploader_id: (data.get('manual_uploader_id') as string) || null,
					thumbnail_url: (data.get('manual_thumbnail_url') as string) || null,
					work_width: data.get('manual_width')
						? +(data.get('manual_width') as string)
						: null,
					work_height: data.get('manual_height')
						? +(data.get('manual_height') as string)
						: null,
					work_duration: data.get('manual_duration')
						? +(data.get('manual_duration') as string)
						: null,
					published_date: (data.get('manual_date') as string) || null
				};
			}
		}

		if (editing_unavailable_source && metadata) {
			const { data: work_id, error: putError } = await rawClient.PUT('/api/upload/source', {
				fetch,
				params: { query: { source_id: source! } },
				body: metadata
			});
			if (putError)
				return fail(400, {
					url: link,
					origin: is_official,
					failed: true,
					code: putError.code,
					errorData: putError.data ?? {}
				});

			redirect(303, `/work/${work_id}`);
		}

		const { data: result, error: postError } = await rawClient.POST('/api/upload/source', {
			fetch,
			params: {
				query: {
					url: link,
					is_reupload: !is_official,
					work_id: work ?? undefined
				}
			},
			body: metadata
		});
		if (postError)
			return fail(400, {
				url: link,
				origin: is_official,
				failed: true,
				code: postError.code,
				errorData: postError.data ?? {}
			});

		// Source already has a work -> redirect to work page
		if (result.work_id) redirect(303, `/work/${result.work_id}`);

		// New source -> redirect to source page (for review/work creation)
		if (result.source_id) redirect(303, `/upload/${result.source_id}`);

		// Fallback
		if (locals.user) redirect(303, `/profile/${locals.user.username}/submissions`);
		else redirect(303, '/login');
	}
} satisfies Actions;
