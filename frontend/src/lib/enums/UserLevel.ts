import { m } from '$lib/paraglide/messages.js';
import { Levels } from '$lib/schema';

export const UserLevelNames = {
	[Levels.Anonymous]: m.heroic_busy_shrimp_lend,
	[Levels.Restricted]: m.fancy_formal_falcon_quell,
	[Levels.Member]: m.drab_alive_midge_edit,
	[Levels.Editor]: m.tasty_spry_firefox_fall,
	[Levels.Admin]: m.silly_blue_felix_amuse,
	[Levels.Owner]: m.tangy_formal_lionfish_tap
} as const satisfies Record<Levels, () => string>;

/**
 * user level `target` has greather level than or equal to `level`
 *
 * @param user_level
 * @param limit
 * @returns
 */
export const hasUserLevel = (user_level: Levels | null | undefined, limit: Levels): boolean => {
	return !!user_level && user_level >= limit;
};
