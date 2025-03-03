import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";
import client, { forwardCookies } from "$lib/api";

export const load: PageServerLoad = async ({cookies, fetch, locals}) => {
    if (locals.user)
        redirect(303, base);

    const { response } = await client.GET('/api/auth/csrf', { fetch });
    forwardCookies(cookies, response);
};

export const actions = {
    default: async ({ cookies, request, fetch, locals }) => {
        const data = await request.formData();
        const username = data.get('username') as string,
            password = data.get('password') as string;

        if (!username || !password)
            return fail(400, { username, missing: true });

		const { response, error } = await client.POST('/api/auth/login', { fetch,
			params: { query: { username, password } },
			headers: { 'X-CSRFToken': cookies.get('csrftoken') }
        });
		if (error)
            return fail(400, { username, failed: true });
        
        forwardCookies(cookies, response);

        const status = await client.GET('/api/auth/status', { fetch });
        if (status.data)
            locals.user = { csrf: cookies.get('csrftoken')!, ...status.data };
    }
} satisfies Actions;
