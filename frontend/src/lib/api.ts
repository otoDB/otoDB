import createClient from "openapi-fetch";
import type { paths } from "./schema";
import { PUBLIC_BACKEND_URL_INTERNAL, PUBLIC_BACKEND_URL_EXTERNAL } from '$env/static/public';
import { browser } from "$app/environment";
import type { Cookies } from "@sveltejs/kit";
import setCookie from "set-cookie-parser";

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

export const forwardCookies = (cookies: Cookies, response: Response) => {
    for (const { name, value, expires, maxAge, sameSite } of setCookie.parse(response.headers.getSetCookie()))
        cookies.set(name, value, {path: '/', expires, maxAge, sameSite});
};
