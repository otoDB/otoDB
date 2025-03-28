import { commentClient } from '$lib/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, parent }) => {
	const data = await parent();
	const comments = await commentClient.GET('account', data.profile.id!, fetch);
	return { comments };
};
