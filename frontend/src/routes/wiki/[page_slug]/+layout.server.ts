import client from '$lib/api.server';
import { languages } from '$lib/enums/language';
import { hasUserLevel } from '$lib/enums/userLevel';
import { markdownExcerpt } from '$lib/markdown';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';
import { Levels } from '$lib/schema';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ params, fetch, locals }) => {
	const { data } = await client.GET('/api/wiki/page', {
		fetch,
		params: { query: { page_slug: params.page_slug } }
	});
	const wiki_page = data ?? [];

	const canEdit = hasUserLevel(locals.user?.level, Levels.Mod);

	const localized = wiki_page.find((p) => p.lang === languages[getLocale()].id) ?? wiki_page[0];

	return {
		page_slug: params.page_slug,
		wiki_page,
		head: {
			title: wiki_page.find((p) => p.title)?.title ?? params.page_slug,
			description: localized ? markdownExcerpt(localized.page) : null
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
