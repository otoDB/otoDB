import type { LayoutServerLoad } from './$types';
import { error } from '@sveltejs/kit';
import client from '$lib/api';
import { m } from '$lib/paraglide/messages';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
	const sourceId = +params.source_id;
	if (isNaN(sourceId)) error(400, { message: 'Bad request' });

	const { data: source, error: e } = await client.GET('/api/upload/source', {
		fetch,
		params: { query: { source_id: sourceId } }
	});

	if (e) error(404, { message: 'Not found' });

	return {
		source,
		sourceId,
		links: [
			{
				pathname: `upload/${sourceId}`,
				title: m.extra_brave_tapir_skip() + ' ' + sourceId
			}
		],
		head: {
			title: m.extra_brave_tapir_skip() + ' ' + sourceId
		}
	};
};
