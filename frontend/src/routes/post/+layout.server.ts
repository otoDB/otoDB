import type { LayoutServerLoad } from './$types';
import { m } from '$lib/paraglide/messages.js';

export const load: LayoutServerLoad = async () => {
	return {
		links: [
			{ pathname: 'post/overview', title: m.just_salty_anaconda_nourish() },
			{ pathname: `post/new`, title: m.antsy_aloof_horse_grace() },
			{ pathname: `post/search`, title: m.mean_top_antelope_love() }
		]
	};
};
