import type { LayoutServerLoad } from "./$types";
import { UserLevel } from "$lib/enums";
import userLevelGuard from "$lib/route_guard";

export const load: LayoutServerLoad = async ({ locals, url }) => {
    userLevelGuard(locals.user, UserLevel.MODERATOR, url.pathname);

    return {
        links: [
            { pathname: `work/unbound`, title: "Pending sources" },
            { pathname: `work/unbound/rejected`, title: "Rejected sources" }
        ]
    };
};
