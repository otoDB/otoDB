import client from '$lib/api.server';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages';
import { Levels } from '$lib/schema';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ params, fetch, locals }) => {
	const { data } = await client.GET('/api/wiki/page', {
		fetch,
		params: { query: { page_slug: params.page_slug } }
	});
	const wiki_page = data ?? [];

	const canEdit = hasUserLevel(locals.user?.level, Levels.Mod);

	return {
		page_slug: params.page_slug,
		wiki_page,
		head: {
			title: wiki_page.find((p) => p.title)?.title ?? params.page_slug
		},
		menuLinks: [
			{
				pathname: `wiki/${params.page_slug}`,
				title: m.curly_zesty_pelican_aim()
			},
			...(canEdit
				? [
						{
							pathname: `wiki/${params.page_slug}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					]
				: []),
			{
				pathname: `wiki/${params.page_slug}/history`,
				title: m.giant_away_scallop_hike()
			}
		]
	};
};
