import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// Revisions index moved from /revision/history to /revision
export const load: PageServerLoad = ({ url }) => {
	redirect(301, `/revision${url.search}`);
};
