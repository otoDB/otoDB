import { fail, type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import client from '$lib/api.server';
import clientRaw from '$lib/api';
import { forwardCookies } from '$lib/api.server';
import { m } from '$lib/paraglide/messages';

export const load: PageServerLoad = async ({ cookies, fetch, locals, url }) => {
	let token = undefined;
	if (!locals.user) {
		token = url.searchParams.get('token');
		const { response } = await client.GET('/api/auth/csrf', { fetch });
		forwardCookies(cookies, response);
	}
	return { token, head: { title: m.true_tough_butterfly_sew() } };
};

export const actions = {
	reset: async ({ request, fetch }) => {
		const data = await request.formData();
		const password = data.get('password') as string,
			confirm = data.get('confirm') as string,
			token = data.get('token') as string;

		if (!password || !confirm) return fail(400, { missing: true });
		else if (password != confirm) return fail(400, { mismatch: true });

		const { error } = await clientRaw.POST('/api/auth/reset_password', {
			body: { password, token },
			fetch
		});

		if (!error) return { reset_success: true };
	},
	request: async ({ request, fetch }) => {
		const data = await request.formData();
		const email = data.get('email') as string;

		if (!email) return fail(400, { missing: true });

		await client.PUT('/api/auth/reset_password', {
			body: { email },
			fetch
		});

		return { success: true };
	}
} satisfies Actions;
