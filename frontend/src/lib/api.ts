import createClient from "openapi-fetch";
import type { paths } from "./schema";
import { PUBLIC_BACKEND_URL_INTERNAL, PUBLIC_BACKEND_URL_EXTERNAL } from '$env/static/public';
import { browser } from "$app/environment";
import type { Cookies } from "@sveltejs/kit";
import setCookie from "set-cookie-parser";

const backend = browser ? PUBLIC_BACKEND_URL_EXTERNAL : PUBLIC_BACKEND_URL_INTERNAL;

const client = createClient<paths>({ baseUrl: backend, credentials: 'include' });
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

export type CommentModels = 'mediawork' | 'account' | 'pool' | 'tagwork' | 'tagsong';

export const commentClient = {
    GET: async (model: CommentModels, pk: number, fetch, opts?) => {
        const comments = await (await fetch(`${backend}comments/api/${model === 'account' ? 'account-account' : `otodb-${model}`}/${pk}/`, { ...opts, method: 'GET' })).json();
        if (comments.length === 0)
            return [];
        else {
            let keep = Object.entries(Object.groupBy(
                comments.filter(e => !e.is_removed).map(({is_removed, permalink, user_avatar, user_url, allow_reply, submit_date, ...keep}) => ({time: new Date((+submit_date) * 1000), ...keep})),
                e => e.level
            )).toSorted((a,b)=>b[0]-a[0]).map(v => v[1]);
            keep.slice(1).forEach((_, i) => keep[i + 1] = keep[i + 1].map(c => ({...c, children: keep[i]?.filter(e => e.parent_id === c.id) ?? []})));
            return keep.at(-1);
        }
    },
    POST: async (model: CommentModels, pk: number, comment: string, reply_to: number, user, fetch, opts?) => (await fetch(`${backend}comments/api/comment/`, { ...opts, method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-CSRFToken': user.csrf },
        body: new URLSearchParams({
            content_type: model === 'account' ? 'otodb.account.account' : `otodb.${model}`,
            object_pk: pk.toString(),
            comment, reply_to: reply_to.toString(),
            name: '', email: 'a@a.co' // will be discarded
        }),
        credentials: 'include'
    })).json()
};
