import { m } from '$lib/paraglide/messages.js';

export const CreatorRole = {
	AUDIO: {
		id: 1,
		nameFn: m.weary_yummy_lobster_kick
	},
	VISUALS: {
		id: 2,
		nameFn: m.great_flaky_spider_comfort
	},
	DIRECTOR: {
		id: 4,
		nameFn: m.brief_slow_robin_fond
	},
	MUSIC: {
		id: 8,
		nameFn: m.known_green_jackal_jolt
	},
	ARTWORK: {
		id: 16,
		nameFn: m.weird_quaint_jan_dazzle
	},
	THANKS: {
		id: 32,
		nameFn: m.heavy_blue_parrot_mend
	}
} as const;

/**
 * @@deprecated
 */
export const resolveCreatorRoleById = (
	id: number
	// (typeof CreatorRole)[keyof typeof CreatorRole]['id']
): (typeof CreatorRole)[keyof typeof CreatorRole] => {
	return Object.values(CreatorRole).find((c) => c.id === id)!;
};
