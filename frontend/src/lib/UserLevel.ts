import { m } from '$lib/paraglide/messages.js';

export const UserLevel = {
	ANONYMOUS: {
		id: 0,
		nameFn: m.heroic_busy_shrimp_lend
	},
	RESTRICTED: {
		id: 10,
		nameFn: m.fancy_formal_falcon_quell
	},
	MEMBER: {
		id: 20,
		nameFn: m.drab_alive_midge_edit
	},
	EDITOR: {
		id: 40,
		nameFn: m.tasty_spry_firefox_fall
	},
	ADMIN: {
		id: 50,
		nameFn: m.silly_blue_felix_amuse
	},
	OWNER: {
		id: 100,
		nameFn: m.tangy_formal_lionfish_tap
	}
} as const;

/**
 * @@deprecated
 */
export const resolveUserLevelById = (
	id: number
	// (typeof UserLevel)[keyof typeof UserLevel]['id']
): keyof typeof UserLevel =>
	Object.entries(UserLevel).find(([_, value]) => value.id === id)?.[0] as keyof typeof UserLevel;
