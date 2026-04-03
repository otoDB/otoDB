import type { LayoutServerLoad } from './$types';
import { m } from '$lib/paraglide/messages.js';
import client from '$lib/api';
import { error } from '@sveltejs/kit';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
	const revision_id = +params.id;
	if (isNaN(revision_id)) error(400, { message: 'Bad request' });

	const { data: revision } = await client.GET('/api/history/revision', {
		fetch,
		params: { query: { revision_id } }
	});
	if (!revision) error(404, { message: 'Not found' });

	return {
		links: [
			{
				pathname: `revision/${params.id}`,
				title: `${m.arable_direct_swan_glow()} #${params.id}`
			},
			{
				pathname: `revision/${params.id}/threads`,
				title: m.big_tiny_kitten_devour()
			}
		],
		revision
	};
};
