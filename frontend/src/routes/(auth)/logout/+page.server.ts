import client from "$lib/api";
import { redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { base } from "$app/paths";

export const load: PageServerLoad = async ({ request, cookies, fetch, locals }) => {
	if (!locals.user)
		redirect(303, base);

	const { error } = await client.POST('/api/auth/logout', { fetch });

	if (!error){
		cookies.delete('csrftoken', {path: '/'});
		cookies.delete('sessionid', {path: '/'});
	}

	redirect(303, base);
}
