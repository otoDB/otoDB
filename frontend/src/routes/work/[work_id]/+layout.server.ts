import client from '$lib/api.server';
import { getDisplayText } from '$lib/ui';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages.js';
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { Levels, Rating } from '$lib/schema';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const { data } = await client.GET('/api/work/work', {
		params: {
			query: {
				work_id: params.work_id
			}
		},
		fetch
	});

	if (data.id !== params.work_id)
		redirect(
			303,
			url.pathname.replace(encodeURIComponent(params.work_id), encodeURIComponent(data.id))
		);

	const loggedOut = !hasUserLevel(locals.user?.level, Levels.Member);

	return {
		links: [
			{
				pathname: `work/${params.work_id}`,
				title: m.grand_merry_fly_succeed() + ' ' + params.work_id
			},
			...(loggedOut
				? []
				: [
						{
							pathname: `work/${params.work_id}/tags`,
							title: m.empty_legal_chicken_taste()
						}
					]),
			...(data.relations[0].length
				? [
						{
							pathname: `work/${params.work_id}/relations`,
							title: m.alive_these_jay_pick()
						}
					]
				: []),
			...(loggedOut
				? []
				: [{ pathname: `work/${params.work_id}/edit`, title: m.minor_crisp_cobra_list() }]),
			{
				pathname: `work/${params.work_id}/threads`,
				title: m.big_tiny_kitten_devour()
			},
			{
				pathname: `work/${params.work_id}/history`,
				title: m.giant_away_scallop_hike()
			},
			{
				pathname: `work/${params.work_id}/moderation`,
				title: m.minor_inner_lynx_adapt()
			}
		],
		...data,
		head: {
			title: getDisplayText(data.title),
			image: data.rating <= 1 ? data.thumbnail : null,
			isExplicit: data.rating === Rating.Explicit,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.grand_merry_fly_succeed(), url: '/work' },
				{ name: getDisplayText(data.title), url: `/work/${params.work_id}` }
			]
		}
	};
};
