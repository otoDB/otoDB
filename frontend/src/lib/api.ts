import createClient from "openapi-fetch";
import type { paths } from "./schema";

const client = createClient<paths>({ baseUrl: "http://127.0.0.1:8000/", credentials: 'include' });
export default client;

export const setToken = (token: string) => {
    client.use({
        async onRequest({ request }) {
            request.headers.set('X-CSRFToken', token);
            return request;
        },
    });
};
