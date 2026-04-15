import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client, { forwardCookies } from '$lib/api';
import { m } from '$lib/paraglide/messages.js';

export const load: PageServerLoad = async ({ cookies, fetch, locals }) => {
	if (locals.user) redirect(303, '/');

	const { response } = await client.GET('/api/auth/csrf', { fetch });
	forwardCookies(cookies, response);
	return { head: { title: m.blue_whole_camel_type() } };
};

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		const data = await request.formData();
		const username = data.get('username') as string,
			invite = data.get('invite') as string,
			email = data.get('email') as string,
			password = data.get('password') as string,
			confirm = data.get('confirm') as string;

		if (!username || !email || !password || !confirm)
			return fail(400, { username, email, missing: true });
		else if (password != confirm) return fail(400, { username, email, mismatch: true });

		const { response, error } = await client.POST('/api/auth/register', {
			body: { username, password, email, invite },
			headers: { 'X-CSRFToken': cookies.get('csrftoken') },
			fetch
		});

		if (response.status === 409) {
			return fail(409, {
				username,
				failed: true,
				message: m.red_raw_duck_evoke()
			});
		}
		if (error)
			return fail(400, {
				username,
				failed: true,
				message: 'An unknown error occurred'
			});

		forwardCookies(cookies, response);
	}
} satisfies Actions;
