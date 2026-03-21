import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	// Kept for backward compatibility with old otoDB browser extension versions
	redirect(301, `/upload/add${url.search}`);
};
