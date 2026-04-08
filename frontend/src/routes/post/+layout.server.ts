import { hasUserLevel, resolveUserLevelById } from '$lib/enums/UserLevel';
import { m } from '$lib/paraglide/messages.js';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		links: [
			{ pathname: 'post/overview', title: m.just_salty_anaconda_nourish() },
			...(locals.user && hasUserLevel(resolveUserLevelById(locals.user.level), 'MEMBER')
				? []
				: [{ pathname: `post/new`, title: m.antsy_aloof_horse_grace() }]),
			{ pathname: `post/search`, title: m.mean_top_antelope_love() }
		]
	};
};
