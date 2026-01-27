import { m } from '$lib/paraglide/messages.js';
import client from '$lib/api';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { userLevelCheck } from '$lib/route_guard';
import { getTagDisplayName } from '$lib/api';

export const load: LayoutServerLoad = async ({ params, fetch, locals }) => {
	const { data, error: e } = await client.GET('/api/tag/song_tag', {
		params: {
			query: {
				tag_slug: params.tag_slug!
			}
		},
		fetch
	});
	if (e) error(404, { message: 'Not found' });

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
			...(userLevelCheck(locals.user)
				? []
				: [
						{
							pathname: `song_attribute/${params.tag_slug}/edit`,
							title: m.minor_crisp_cobra_list()
						}
					])
		],
		tag: data,
		...details,
		display_name: getTagDisplayName(data)
	};
};
