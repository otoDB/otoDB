import client from '$lib/api';
import { commentClient } from '$lib/api';
import type { PageServerLoad } from '../../[tag_slug]/$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const { data: songs } = await client.GET('/api/tag/songs', {
		fetch,
		params: {
			query: {
				tag_slug: params.tag_slug
			}
		}
	});

	const comments = await commentClient.GET('tagsong', data.tag.id, fetch);

	return {
		songs,
		comments
	};
};
