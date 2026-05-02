import { env } from '$env/dynamic/public';
import createClient from 'openapi-fetch';
import { parseApiErrorResponse } from '$lib/errors';
import type { paths } from '$lib/schema';
import { callApiErrorToast } from '$lib/toast';

export const client = createClient<paths>({
	baseUrl: env.PUBLIC_API_ENDPOINT,
	credentials: 'include'
});
client.use({
	onResponse: async ({ response }) => {
		if (!response.ok) {
			const err = await parseApiErrorResponse(response);
			callApiErrorToast(err);
		}
		return response;
	}
});
export const rawClient = createClient<paths>({
	baseUrl: env.PUBLIC_API_ENDPOINT,
	credentials: 'include'
});
export default client;
