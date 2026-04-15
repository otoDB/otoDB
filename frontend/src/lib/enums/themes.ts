import { m } from '$lib/paraglide/messages';

export const themes = {
	'default': { id: 0, nameFn: m.grassy_noble_walrus_wish },
	'aniki': { id: 1, nameFn: m.next_ago_opossum_swim },
	'otogroove': { id: 2, nameFn: () => 'otogroove' },
	'retro-voyage': { id: 3, nameFn: m.tiny_plane_ape_pull },
	'sorimix': { id: 4, nameFn: m.mean_zesty_ray_savor },
	'resample': { id: 5, nameFn: () => 'Re:Sample' }
} as const satisfies Record<string, { id: number; nameFn: () => string }>;

/**
 * @deprecated そもそもテーマIDを数値として扱うのを止めるべきだ．
 */
export const getThemeNameById = (id: number): keyof typeof themes => {
	const theme = Object.entries(themes).find(([_, value]) => value.id === id)?.[0];
	return theme ? (theme as keyof typeof themes) : 'default';
};
