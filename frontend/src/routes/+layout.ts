import { browser } from '$app/environment';
import client from '$lib/api';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = ({ data }) => {
	if (browser && data?.user?.csrf) {
		const token = data?.user?.csrf;
		client.use({
			async onRequest({ request }) {
				request.headers.set('X-CSRFToken', token);
				return request;
			}
		});
	}
	return data;
};
