import client from "$lib/api";
import { error } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ fetch, params }) => {
    if (isNaN(+params.list_id))
        error(400, { message: 'Bad request' });
    
    const { data, error: e } = await client.GET('/api/list/list', { fetch,
        params: {
            query: {
                list_id: +params.list_id
            }
        }
    });
    if (e)
        error(404, { message: 'Not found' });

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
