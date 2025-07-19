import { m } from '$lib/paraglide/messages.js';
import client from '$lib/api';
import type { LayoutServerLoad } from './$types';
import { error, redirect } from '@sveltejs/kit';
import { userLevelCheck } from '$lib/route_guard';
import { getTagDisplayName } from '$lib/api';

export const load: LayoutServerLoad = async ({ params, fetch, locals, url }) => {
	const {
		data,
		error: e,
		response
	} = await client.GET('/api/tag/tag', {
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

	return {
		links: [
			{
				pathname: `tag/${params.tag_slug}`,
				title: m.empty_legal_chicken_taste() + ' ' + params.tag_slug
			},
			...(userLevelCheck(locals.user)
				? []
				: [{ pathname: `tag/${params.tag_slug}/edit`, title: m.minor_crisp_cobra_list() }])
		],
		song_links: data.song
			? [
					{
						pathname: `tag/${params.tag_slug}`,
						title: m.grand_nice_pony_belong() + ' ' + data.song.title
					},
					...(userLevelCheck(locals.user)
						? []
						: [
								{
									pathname: `tag/${params.tag_slug}/song_tags`,
									title: m.empty_legal_chicken_taste()
								},
								{
									pathname: `tag/${params.tag_slug}/edit`,
									title: m.minor_crisp_cobra_list()
								}
							])
				]
			: null,
		tag: data,
		song_relations,
		display_name: getTagDisplayName(data)
	};
};
