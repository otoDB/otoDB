import { browser } from '$app/environment';
import { env } from '$env/dynamic/public';
import createClient from 'openapi-fetch';
import { parseApiErrorResponse } from '$lib/errors';
import type { paths } from '$lib/schema';
import { callApiErrorToast } from '$lib/toast';

const baseUrl =
	browser && env.PUBLIC_API_PORT
		? `${location.protocol}//${location.hostname}:${env.PUBLIC_API_PORT}/`
		: env.PUBLIC_API_ENDPOINT;

export const client = createClient<paths>({
	baseUrl,
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
	baseUrl,
	credentials: 'include'
});
export default client;
