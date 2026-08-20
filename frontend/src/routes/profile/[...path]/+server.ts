import { redirect, type RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = ({ url }) => {
	redirect(308, `/user${url.pathname.slice('/profile'.length)}${url.search}`);
};
