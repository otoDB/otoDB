import type { LayoutServerLoad } from "./$types";

export const load: LayoutServerLoad = async ({ cookies }) => {
    return {
        session: cookies.get('sessionid'),
        csrf: cookies.get('csrftoken')
    };
};
