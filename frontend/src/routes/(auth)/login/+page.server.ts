import { getAuth } from "$lib/api";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({cookies, fetch}) => {
    const r = await getAuth(cookies, fetch);
    if (r)
        redirect(307, '/');
};
