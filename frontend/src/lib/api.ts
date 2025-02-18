import createClient from "openapi-fetch";
import type { paths } from "./schema";
import { PUBLIC_BACKEND_URL_INTERNAL, PUBLIC_BACKEND_URL_EXTERNAL } from '$env/static/public';
import { browser } from "$app/environment";
import type { Cookies } from "@sveltejs/kit";

const client = createClient<paths>({ baseUrl: 
   browser ? PUBLIC_BACKEND_URL_EXTERNAL : PUBLIC_BACKEND_URL_INTERNAL,
   credentials: 'include'
});
export default client;

export const setToken = (token: string) => {
    if (browser)
        client.use({
            async onRequest({ request }) {
                request.headers.set('X-CSRFToken', token);
                return request;
            },
        });
};

export const getAuth = async (cookies: Cookies, fetch: any) => {
    const session = cookies.get('sessionid'),
        csrf = cookies.get('csrftoken');
    if (!session || !csrf)
        return null;

    const status = await client.GET('/api/auth/status', { fetch });
    if (!status.data)
        return null;

    return { csrf: csrf, data: status.data };
}
