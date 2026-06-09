import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

// Threads moved from /post to /thread
export const load: PageServerLoad = ({ params, url }) => {
	const rest = params.rest ? `/${params.rest}` : '';
	redirect(301, `/thread${rest}${url.search}`);
};
