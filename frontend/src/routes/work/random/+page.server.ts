import client from "$lib/api";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ fetch }) => {
    const { data: random } = await client.GET('/api/work/random', { fetch });
    if (random)
        redirect(303, `${base}/work/${random.id}`);
    else
        redirect(303, base);
};
