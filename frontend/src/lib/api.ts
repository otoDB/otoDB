import createClient from "openapi-fetch";
import type { paths } from "./schema";

// TODO: Read this from an environment variable
const client = createClient<paths>({ baseUrl: "http://127.0.0.1:8000/", credentials: 'include' });
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
