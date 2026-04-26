import client from '$lib/api.server';
import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';
import { getTagDisplayName } from '$lib/ui';
import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const { data } = await client.GET('/api/tag/song_tag', {
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

	const { data: details } = await client.GET('/api/tag/song_tag_details', {
		fetch,
		params: {
			query: {
				tag_slug: params.tag_slug
			}
		}
	});

	return {
		links: [
			{
				pathname: `song_attribute/${params.tag_slug}`,
				title: m.dull_plain_angelfish_cuddle() + ' ' + params.tag_slug
			},
			...(hasUserLevel(locals.user?.level, Levels.Member)
				? [
						{
							pathname: `song_attribute/${params.tag_slug}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					]
				: []),

			{
				pathname: `song_attribute/${params.tag_slug}/history`,
				title: m.giant_away_scallop_hike()
			}
		],
		tag: data,
		...details,
		display_name: getTagDisplayName(data),
		head: {
			title: getTagDisplayName(data),
			breadcrumbs: [
				{ name: m.fine_late_chicken_quiz(), url: '/' },
				{ name: m.dull_plain_angelfish_cuddle(), url: '/song_attribute' },
				{ name: getTagDisplayName(data), url: `/song_attribute/${params.tag_slug}` }
			]
		}
	};
};
