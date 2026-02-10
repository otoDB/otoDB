import { m } from '$lib/paraglide/messages.js';
import client from '$lib/api';
import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import { userLevelCheck } from '$lib/route_guard';
import { getTagDisplayName } from '$lib/api';
import { redirect } from '@sveltejs/kit';

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
				encodeURIComponent(e as string)
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
					]),

			{
				pathname: `song_attribute/${params.tag_slug}/history`,
				title: m.giant_away_scallop_hike()
			}
		],
		tag: data,
		...details,
		display_name: getTagDisplayName(data),
		head: {
			title: m.mild_loud_shad_enchant({
				type: m.dull_plain_angelfish_cuddle(),
				name: data.name
			})
		}
	};
};
