import client, { getDisplayText } from '$lib/api';
import { hasUserLevel, resolveUserLevelById } from '$lib/enums/UserLevel';
import { m } from '$lib/paraglide/messages.js';
import { error, redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	if (isNaN(+params.work_id)) error(400, { message: 'Bad request' });

	const {
		data,
		error: e,
		response
	} = await client.GET('/api/work/work', {
		params: {
			query: {
				work_id: +params.work_id
			}
		},
		fetch
	});

	if (response.status === 300)
		redirect(
			303,
			url.pathname.replace(
				encodeURIComponent(params.work_id),
				encodeURIComponent(e as unknown as string)
			)
		);
	if (e) error(404, { message: 'Not found' });

	const loggedOut = !(
		locals.user && hasUserLevel(resolveUserLevelById(locals.user.level), 'MEMBER')
	);

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
			}
		],
		...data,
		head: {
			title: getDisplayText(data.title),
			image: data.rating <= 1 ? data.thumbnail : null,
			isExplicit: data.rating === 2,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.grand_merry_fly_succeed(), url: '/work/search' },
				{ name: getDisplayText(data.title), url: `/work/${params.work_id}` }
			]
		}
	};
};
