import client from '$lib/api';
import { PathsApiProfileSubmissionsGetParametersQueryOrderAnyOf0 } from '$lib/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params, url }) => {
	const batch_size = 30;
	const page = parseInt(url.searchParams.get('page') ?? '0', 10) || 1;
	const platform = parseInt(url.searchParams.get('platform') ?? '', 10) || null,
		origin = parseInt(url.searchParams.get('origin') ?? '', 10) || null,
		status = parseInt(url.searchParams.get('status') ?? '', 10) || null,
		standing = parseInt(url.searchParams.get('standing') ?? '1', 10) || 0;

	const paramDir = url.searchParams.get('dir') === '-' ? '-' : '';
	const paramOrder = `${paramDir}${url.searchParams.get('order')}`;

	type Order = PathsApiProfileSubmissionsGetParametersQueryOrderAnyOf0;
	const order: Order | null =
		paramOrder &&
		Object.values(PathsApiProfileSubmissionsGetParametersQueryOrderAnyOf0).includes(
			paramOrder as Order
		)
			? (paramOrder as Order)
			: null;

	const { data: submissions } = await client.GET('/api/profile/submissions', {
		fetch,
		params: {
			query: {
				username: params.username,
				limit: batch_size,
				offset: (page - 1) * batch_size,
				order: order,
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
		dir: paramDir,
		standing
	};
};
