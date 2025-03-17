import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";
import client from "$lib/api";

export const load: PageServerLoad = async ({ params, parent, fetch }) => {
    const data = await parent();
    if (data.list?.author?.username !== data.user?.username)
        redirect(303, `${base}/list/${params.list_id}`);
    
    if (data.list.id) {
        await client.DELETE('/api/list/list', { fetch, params: { query: { list_id: data.list.id }} });
        redirect(303, `${base}/profile/${data.user?.username}/lists`);
    }
    else
        redirect(303, base);
}
