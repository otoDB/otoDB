import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies, fetch, locals }) => {
	if (locals.user)
		return {
			user: locals.user
		};
};
