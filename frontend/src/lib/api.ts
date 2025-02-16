import createClient from "openapi-fetch";
import type { paths } from "./schema";
import {
    BACKEND_URL,
} from '$env/static/private';

const client = createClient<paths>({ baseUrl: BACKEND_URL, credentials: 'include' });
export default client;

// N.B. USE ON CLIENT ONLY! DO NOT USE THIS ON THE SERVER
export const setToken = (token: string) => {
    client.use({
        async onRequest({ request }) {
            request.headers.set('X-CSRFToken', token);
            return request;
        },
    });
};
