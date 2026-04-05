import { m } from '$lib/paraglide/messages.js';

export const mediaTypes = {
	ANIME: {
		id: 1,
		nameFn: m.sea_new_barbel_rest
	},
	SHOW: {
		id: 2,
		nameFn: m.every_vivid_dolphin_dash
	},
	FILM: {
		id: 4,
		nameFn: m.drab_gaudy_fly_relish
	},
	GAME: {
		id: 8,
		nameFn: m.maroon_close_gorilla_bake
	}
} as const;

export const allMediaTypes: (keyof typeof mediaTypes)[] = ['ANIME', 'SHOW', 'FILM', 'GAME'];

/**
 * @deprecated
 */
export const resolveMediaTypeKeyById = (
	id: number // (typeof mediaTypes)[keyof typeof mediaTypes]['id']
): keyof typeof mediaTypes => {
	return Object.entries(mediaTypes).find(([_, v]) => v.id === id)?.[0] as keyof typeof mediaTypes;
};
