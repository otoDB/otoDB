import client from '$lib/api.server';
import { m } from '$lib/paraglide/messages';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, url }) => {
	const status = url.searchParams.get('status') === 'closed' ? 'closed' : 'open';

	const { data } = await client.GET('/api/thread/categories', {
		fetch,
		params: {
			query: { is_open: status === 'open' }
		}
	});
	return {
		status,
		categories: data!,
		head: { title: m.just_salty_anaconda_nourish() }
	};
};
