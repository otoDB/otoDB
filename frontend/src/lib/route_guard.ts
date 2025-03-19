import { redirect } from "@sveltejs/kit";
import { UserLevel } from "./enums";

const userLevelGuard = (user: App.Locals['user'], userlevel = UserLevel.MEMBER, from: string, to = '/login') => {
    if (!user || user.level < UserLevel.MEMBER)
        redirect(303, to === '/login' && from ? `${to}?from=${from}` : to)
};

export default userLevelGuard;
