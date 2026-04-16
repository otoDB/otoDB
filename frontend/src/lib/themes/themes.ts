import { m } from '$lib/paraglide/messages';
import previewAniki from '$lib/themes/aniki.png';
import previewOtogroove from '$lib/themes/otogroove.png';
import previewRetroVoyage from '$lib/themes/retro-voyage.png';
import previewSorimix from '$lib/themes/sorimix.png';
import previewResample from '$lib/themes/resample.png';

export const themes = {
	'default': { id: 0, nameFn: m.grassy_noble_walrus_wish, preview: null },
	'aniki': { id: 1, nameFn: m.next_ago_opossum_swim, preview: previewAniki },
	'otogroove': { id: 2, nameFn: () => 'otogroove', preview: previewOtogroove },
	'retro-voyage': { id: 3, nameFn: m.tiny_plane_ape_pull, preview: previewRetroVoyage },
	'sorimix': { id: 4, nameFn: m.mean_zesty_ray_savor, preview: previewSorimix },
	'resample': { id: 5, nameFn: () => 'Re:Sample', preview: previewResample }
} satisfies Record<string, { id: number; nameFn: () => string; preview: null | string }>;

/**
 * @deprecated そもそもテーマIDを数値として扱うのを止めるべきだ．
 */
export const getThemeNameById = (id: number): keyof typeof themes => {
	const theme = Object.entries(themes).find(([_, value]) => value.id === id)?.[0];
	return theme ? (theme as keyof typeof themes) : 'default';
};
