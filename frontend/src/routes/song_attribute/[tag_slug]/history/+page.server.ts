import client from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, fetch }) => {
	const { data: history } = await client.GET('/api/history/history', {
		fetch,
		params: {
			query: {
				entity: 'tagsong',
				id: params.tag_slug
			}
		}
	});

	// TODO: Error forwarding
	if (!history) error(500, 'Failed to fetch data.');

	return {
		history
	};
};
