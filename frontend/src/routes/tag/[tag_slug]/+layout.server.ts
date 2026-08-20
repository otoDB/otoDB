import client from '$lib/api.server';
import { getTagDisplayName } from '$lib/ui';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages.js';
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { Levels, WorkTagCategory } from '$lib/schema';

const TITLE_BY_CATEGORY: Partial<Record<WorkTagCategory, (args: { name: string }) => string>> = {
	[WorkTagCategory.Creator]: m.brave_misty_lark_glow,
	[WorkTagCategory.Song]: m.sunny_civil_moth_drum,
	[WorkTagCategory.Source]: m.witty_late_heron_bake,
	[WorkTagCategory.Event]: m.quick_famous_otter_wave
};

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const { data } = await client.GET('/api/tag/tag', {
		params: {
			query: {
				tag_slug: params.tag_slug!
			}
		},
		fetch
	});

	if (data.slug !== params.tag_slug)
		redirect(
			303,
			url.pathname.replace(encodeURIComponent(params.tag_slug), encodeURIComponent(data.slug))
		);

	const song_relations = data.song
		? (
				await client.GET('/api/tag/song_relations', {
					fetch,
					params: {
						query: {
							song_id: data.song.id
						}
					}
				})
			).data
		: null;
	const display_name = getTagDisplayName(data);
	return {
		links: [
			{
				pathname: `tag/${params.tag_slug}`,
				title: m.empty_legal_chicken_taste() + ' ' + params.tag_slug
			},
			...(hasUserLevel(locals.user?.level, Levels.Member)
				? [
						{
							pathname: `tag/${params.tag_slug}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					]
				: []),
			{
				pathname: `tag/${params.tag_slug}/threads`,
				title: m.big_tiny_kitten_devour()
			},
			{
				pathname: `tag/${params.tag_slug}/history`,
				title: m.giant_away_scallop_hike()
			}
		],
		song_links: data.song
			? [
					{
						pathname: `tag/${params.tag_slug}`,
						title: m.grand_nice_pony_belong() + ' ' + data.song.id
					},
					...(hasUserLevel(locals.user?.level, Levels.Member)
						? [
								{
									pathname: `tag/${params.tag_slug}/song_tags`,
									title: m.dull_plain_angelfish_cuddle()
								},
								{
									pathname: `tag/${params.tag_slug}/edit`,
									title: m.minor_crisp_cobra_list()
								}
							]
						: []),
					{
						pathname: `tag/${params.tag_slug}/history`,
						title: m.giant_away_scallop_hike()
					}
				]
			: null,
		tag: data,
		song_relations,
		display_name,
		head: {
			title: (TITLE_BY_CATEGORY[data.category] ?? m.calm_super_finch_note)({ name: display_name }),
			description: m.keen_vivid_snail_march({ name: display_name }),
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.empty_legal_chicken_taste(), url: '/tag' },
				{ name: display_name, url: `/tag/${params.tag_slug}` }
			]
		}
	};
};
