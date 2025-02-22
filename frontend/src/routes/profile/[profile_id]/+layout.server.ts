import { base } from "$app/paths";
import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ params }) => {
    return {
        links: [
            { pathname: `profile/${params.profile_id}`, title: "Profile " + params.profile_id },
            { pathname: `profile/${params.profile_id}/lists`, title: "Lists" }
        ]
    };
};
