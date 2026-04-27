import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import { forwardCookies } from '$lib/api.server';
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

		try {
			const { response } = await client.POST('/api/auth/login', {
				fetch,
				body: { username, password },
				headers: { 'X-CSRFToken': cookies.get('csrftoken') }
			});
			forwardCookies(cookies, response);
		} catch {
			return fail(400, { username, failed: true });
		}
	}
} satisfies Actions;
