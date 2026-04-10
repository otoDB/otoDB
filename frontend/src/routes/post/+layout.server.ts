import type { LayoutServerLoad } from './$types';
import { m } from '$lib/paraglide/messages.js';
import { userLevelCheck } from '$lib/route_guard';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		links: [
			{ pathname: 'post/overview', title: m.just_salty_anaconda_nourish() },
			...(userLevelCheck(locals.user)
				? []
				: [{ pathname: `post/new`, title: m.antsy_aloof_horse_grace() }]),
			{ pathname: `post`, title: m.mean_top_antelope_love() }
		]
	};
};
