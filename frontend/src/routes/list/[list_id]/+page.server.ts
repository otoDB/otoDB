import client from "$lib/api";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ fetch, params }) => {
    const { data, error } = await client.GET('/api/list/list', { fetch,
        params: {
            query: {
                list_id: +params.list_id
            }
        }
    });
    if (error)
        return; // TODO
    const { data: entries } = await client.GET('/api/list/entries', { fetch,
        params: {
            query: {
                list_id: +params.list_id
            }
        }
    });
    return {
        list: data,
        entries
    };
}
