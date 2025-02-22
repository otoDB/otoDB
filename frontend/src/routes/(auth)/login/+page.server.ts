import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";
import client from "$lib/api";
import setCookie from "set-cookie-parser";

export const load: PageServerLoad = async ({cookies, fetch, locals}) => {
    if (locals.user)
        redirect(303, base);
};

export const actions = {
    default: async ({ cookies, request, fetch, locals }) => {
        const data = await request.formData();
        const username = data.get('username') as string, password = data.get('password') as string;

        if (!username || !password)
            return fail(400, { username, missing: true });

        const { response: response_csrf, data: csrf } = await client.GET('/api/auth/csrf', { fetch });
		if (!csrf)
			return;

        const raw_csrf_cookie = response_csrf.headers.getSetCookie();
        const csrf_cookie = setCookie.parse(raw_csrf_cookie)[0];
        cookies.set(csrf_cookie.name, csrf_cookie.value, {
            path: '/',
            expires: csrf_cookie.expires,
            maxAge: csrf_cookie.maxAge,
            sameSite: csrf_cookie.sameSite
        })

		const { response, error } = await client.POST('/api/auth/login', { fetch,
			params: { query: { username, password } },
			headers: { 'X-CSRFToken': csrf['csrf_token'], cookie: raw_csrf_cookie[0] },
        });
		if (error) {
            cookies.delete(csrf_cookie.name, { path: '/' });
            return fail(400, { username, failed: true });
        }
        const responseCookies = setCookie.parse(response.headers.getSetCookie());
        for (const { name, value, expires, maxAge, sameSite } of responseCookies) {
            cookies.set(name, value, {path: '/', expires, maxAge, sameSite});
        }
        const status = await client.GET('/api/auth/status', { fetch });
        if (status.data)
            locals.user = { csrf: cookies.get(csrf_cookie.name)!, ...status.data };
    }
} satisfies Actions;
