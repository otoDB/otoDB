import { env } from '$env/dynamic/public';
import createClient from 'openapi-fetch';
import { parseApiErrorResponse } from '$lib/errors';
import type { paths } from '$lib/schema';
import { callErrorCodeToast } from '$lib/toast';

export const client = createClient<paths>({
	baseUrl: env.PUBLIC_API_ENDPOINT,
	credentials: 'include'
});
client.use({
	onResponse: async ({ response }) => {
		if (!response.ok) {
			const { code, data } = await parseApiErrorResponse(response);
			callErrorCodeToast(code, data);
		}
		return response;
	}
});
export default client;
