import client, { forwardCookies, rawClient } from '$lib/api.server';
import { apiFail } from '$lib/errors';
import { m } from '$lib/paraglide/messages.js';
import { env } from '$env/dynamic/private';
import { fail, redirect, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const inviteRequired = () => env.OTODB_INVITE_REQUIRED?.toLowerCase() === 'true';

export const load: PageServerLoad = async ({ cookies, fetch, locals }) => {
	if (locals.user) redirect(303, '/');

	const { response } = await client.GET('/api/auth/csrf', { fetch });
	forwardCookies(cookies, response);
	return {
		head: { title: m.blue_whole_camel_type() },
		inviteRequired: inviteRequired()
	};
};

export const actions = {
	default: async ({ cookies, request, fetch }) => {
		const data = await request.formData();
		const username = data.get('username') as string,
			email = data.get('email') as string,
			password = data.get('password') as string,
			confirm = data.get('confirm') as string,
			turnstile_token = (data.get('cf-turnstile-response') as string) || undefined;
		const invite = inviteRequired() ? ((data.get('invite') as string) ?? undefined) : undefined;

		if (!username || !email || !password || !confirm)
			return fail(400, { username, email, missing: true });
		else if (password !== confirm) return fail(400, { username, email, mismatch: true });

		const { response, error: apiError } = await rawClient.POST('/api/auth/register', {
			body: { username, password, email, invite, turnstile_token },
			headers: { 'X-CSRFToken': cookies.get('csrftoken') },
			fetch
		});

		if (apiError) return apiFail(apiError, { username, email });

		forwardCookies(cookies, response);
	}
} satisfies Actions;
