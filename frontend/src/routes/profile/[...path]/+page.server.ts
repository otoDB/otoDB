import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ params, url }) => {
	const path = params.path ? `/${params.path}` : '';
	redirect(308, `/user${path}${url.search}`);
};
