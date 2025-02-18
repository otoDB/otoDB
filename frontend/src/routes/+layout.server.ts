import client, { getAuth } from "$lib/api";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
    const r = await getAuth(cookies, fetch);
    if (r)    
        return {
            user: {
                name: r.data.username,
                id: r.data.user_id
            },
            csrf: r.csrf
        };
};
