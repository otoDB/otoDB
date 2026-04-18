import client, { getTagDisplayName } from '$lib/api';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages.js';
import { error, redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { Levels } from '$lib/schema';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const { data, error: e } = await client.GET('/api/tag/tag', {
		params: {
			query: {
				tag_slug: params.tag_slug!
			}
		},
		fetch
	});

	if (e) error(404, { message: 'Not found' });

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
							song_id: +data.song.id
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
				? [{ pathname: `tag/${params.tag_slug}/edit`, title: m.minor_crisp_cobra_list() }]
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
			title: display_name,
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.empty_legal_chicken_taste(), url: '/tag' },
				{ name: display_name, url: `/tag/${params.tag_slug}` }
			]
		}
	};
};
