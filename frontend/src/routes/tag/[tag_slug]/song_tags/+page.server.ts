import client from "$lib/api";
import { UserLevel } from "$lib/enums";
import type { PageServerLoad } from "../$types";
import userLevelGuard from "$lib/route_guard";
import { redirect } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ locals, parent, url }) => {
    userLevelGuard(locals.user, UserLevel.MEMBER, url.pathname);
    const data = await parent();
    if (!data.tag.song)
        redirect(303, `/tag/${data.tag.slug}`);
};
