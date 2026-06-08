import { redirect } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = ({ params, url }) => {
	const suffix = params.rest ? `/${params.rest}` : '';
	redirect(301, `/work/${params.work_id}${suffix}${url.search}`);
};
