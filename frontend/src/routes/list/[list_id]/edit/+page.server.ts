import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ params, parent }) => {
    const data = await parent();
    if (data.list?.author?.username !== data.user?.username)
        redirect(303, `${base}/list/${params.list_id}`);
}
