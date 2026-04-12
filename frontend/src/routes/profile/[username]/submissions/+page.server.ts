import client from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params, url }) => {
	const batch_size = 30;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const platform = parseInt(url.searchParams.get('platform') ?? '', 10) || null,
		origin = parseInt(url.searchParams.get('origin') ?? '', 10) || null,
		status = parseInt(url.searchParams.get('status') ?? '', 10) || null,
		standing = parseInt(url.searchParams.get('standing') ?? '1', 10) || 0;

	const paramDir = url.searchParams.get('dir');
	const dir: '' | '-' = paramDir === '-' ? '-' : '';

	const paramOrder = url.searchParams.get('order');
	const order: 'id' | 'published_date' | null = (() => {
		switch (paramOrder) {
			case 'id':
			case 'published_date':
				return paramOrder;
			default:
				return null;
		}
	})();

	const { data: submissions } = await client.GET('/api/profile/submissions', {
		fetch,
		params: {
			query: {
				username: params.username,
				limit: batch_size,
				offset: (page - 1) * batch_size,
				order: order ? `${dir}${order}` : null,
				origin,
				platform,
				status,
				standing
			}
		}
	});
	return {
		submissions,
		page,
		batch_size,
		order,
		origin,
		platform,
		status,
		dir,
		standing
	};
};
