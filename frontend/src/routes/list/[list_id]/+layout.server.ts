import client from "$lib/api";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, params }) => {
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
