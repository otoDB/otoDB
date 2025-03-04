import { base } from "$app/paths";
import { redirect } from "@sveltejs/kit";
import type { LayoutServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";

export const load: LayoutServerLoad = async ({ locals }) => {
    if (!locals.user || locals.user.level < UserLevel.MODERATOR)
        redirect(303, base);

    return {
        links: [
            { pathname: `work/unbound`, title: "Pending sources" },
            { pathname: `work/unbound/rejected`, title: "Rejected sources" }
        ]
    };
};
