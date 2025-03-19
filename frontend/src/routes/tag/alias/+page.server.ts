import { base } from "$app/paths";
import { redirect } from "@sveltejs/kit";
import { UserLevel } from "$lib/enums";
import type { PageServerLoad } from "../../work/unbound/$types";

export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MODERATOR)
        redirect(303, base);
};
