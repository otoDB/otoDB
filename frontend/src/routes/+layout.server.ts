import client from "$lib/api";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
    const session = cookies.get('sessionid'),
        csrf = cookies.get('csrftoken');
    if (!session || !csrf)
        return;

    const status = await client.GET('/api/auth/status', { fetch });
    if (!status.data)
        return;

    return {
        user: {
            name: status.data.username,
            id: status.data.user_id
        },
        csrf
    };
};
