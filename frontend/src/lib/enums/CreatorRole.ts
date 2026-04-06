import { m } from '$lib/paraglide/messages.js';

export const creatorRole = {
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

export const allCreatorRoles = Object.keys(creatorRole) as (keyof typeof creatorRole)[];

/**
 * @deprecated
 */
export const resolveCreatorRoleKeyById = (
	id: number // (typeof creatorRole)[keyof typeof creatorRole]['id']
): keyof typeof creatorRole => {
	return Object.entries(creatorRole).find(
		([_, v]) => v.id === id
	)?.[0] as keyof typeof creatorRole;
};
