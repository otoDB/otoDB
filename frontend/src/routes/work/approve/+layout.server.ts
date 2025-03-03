import { base } from "$app/paths";
import { redirect } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";

export const load: LayoutServerLoad = async ({ locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MODERATOR)
        redirect(303, base);

    return {
        links: [
            { pathname: `work/approve`, title: "Pending sources" },
            { pathname: `work/approve/rejected`, title: "Rejected sources" }
        ]
    };
};
