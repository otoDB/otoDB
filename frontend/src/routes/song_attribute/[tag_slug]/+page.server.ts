import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch, parent }) => {
	const data = await parent();

	const [{ data: songs }, { data: comments }] = await Promise.all([
		client.GET('/api/tag/songs', {
			fetch,
			params: {
				query: {
					tag_slug: params.tag_slug
				}
			}
		}),
		client.GET('/api/comment/comments', {
			fetch,
			params: { query: { model: 'tagsong', pk: data.tag.id } }
		})
	]);

	// TODO: Error forwarding
	if (!songs) error(500, 'Failed to fetch data.');
	if (!comments) error(500, 'Failed to fetch data.');

	return {
		songs,
		comments
	};
};
