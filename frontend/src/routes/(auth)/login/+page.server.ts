import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client, { forwardCookies, rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ cookies, fetch, locals, url }) => {
	if (locals.user) redirect(303, url.searchParams.get('from') ?? '/');

	const { response } = await client.GET('/api/auth/csrf', { fetch });
	forwardCookies(cookies, response);

	return { head: { title: m.inner_stale_anteater_walk() } };
};

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		const data = await request.formData();
		const username = data.get('username') as string,
			password = data.get('password') as string;

		if (!username || !password) return fail(400, { username, missing: true });

		const { response, error: apiError } = await rawClient.POST('/api/auth/login', {
			fetch,
			body: { username, password },
			headers: { 'X-CSRFToken': cookies.get('csrftoken') }
		});
		if (apiError) return apiFail(apiError, { username });
		forwardCookies(cookies, response);
	}
} satisfies Actions;
