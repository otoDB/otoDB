import { hasUserLevel } from '$lib/enums/userLevel';
import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		links: [
			{
				pathname: 'thread/overview',
				title: m.just_salty_anaconda_nourish()
			},
			...(hasUserLevel(locals.user?.level, Levels.Member)
				? [
						{
							pathname: `thread/new`,
							title: m.antsy_aloof_horse_grace()
						}
					]
				: []),
			{ pathname: `thread`, title: m.mean_top_antelope_love() }
		]
	};
};
