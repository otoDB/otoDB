import { m } from '$lib/paraglide/messages.js';
import client from '$lib/api';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';

import { getTagDisplayName } from '$lib/api';
import { redirect } from '@sveltejs/kit';
import { hasUserLevel } from '$lib/enums/UserLevel';
import { Levels } from '$lib/schema';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const {
		data,
		error: e,
		response
	} = await client.GET('/api/tag/song_tag', {
		params: {
			query: {
				tag_slug: params.tag_slug!
			}
		},
		fetch
	});
	if (response.status === 300)
		redirect(
			303,
			url.pathname.replace(
				encodeURIComponent(params.tag_slug),
				encodeURIComponent(e as unknown as string)
			)
		);
	else if (e) error(404, { message: 'Not found' });

	const { data: details } = await client.GET('/api/tag/song_tag_details', {
		fetch,
		params: {
			query: {
				tag_slug: params.tag_slug
			}
		}
	});
	if (!details) error(500, { message: 'Failed to load tag details' });

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
