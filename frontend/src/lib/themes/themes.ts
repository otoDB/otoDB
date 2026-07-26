import { m } from '$lib/paraglide/messages';
import previewAniki from '$lib/themes/aniki.webp';
import previewOtogroove from '$lib/themes/otogroove.webp';
import previewRetroVoyage from '$lib/themes/retro-voyage.webp';
import previewSorimix from '$lib/themes/sorimix.webp';
import previewResample from '$lib/themes/resample.webp';
import previewPlainDark from '$lib/themes/plain-dark.webp';
import previewPlainLight from '$lib/themes/plain-light.webp';
import previewDefault from '$lib/themes/default.webp';
import { ThemePref } from '$lib/schema';

export const themes: Record<ThemePref, { key: string; nameFn: () => string; preview: string }> = {
	[ThemePref.Default]: {
		key: 'default',
		nameFn: m.grassy_noble_walrus_wish,
		preview: previewDefault
	},
	[ThemePref.Plain_Dark]: {
		key: 'plain-dark',
		nameFn: m.hazy_calm_otter_dream,
		preview: previewPlainDark
	},
	[ThemePref.Plain_Light]: {
		key: 'plain-light',
		nameFn: m.misty_plain_finch_glow,
		preview: previewPlainLight
	},
	[ThemePref.Aniki]: {
		key: 'aniki',
		nameFn: m.next_ago_opossum_swim,
		preview: previewAniki
	},
	[ThemePref.otogroove]: {
		key: 'otogroove',
		nameFn: () => 'otogroove',
		preview: previewOtogroove
	},
	[ThemePref.Retro_Voyage]: {
		key: 'retro-voyage',
		nameFn: m.tiny_plane_ape_pull,
		preview: previewRetroVoyage
	},
	[ThemePref.SORIMIX]: {
		key: 'sorimix',
		nameFn: m.mean_zesty_ray_savor,
		preview: previewSorimix
	},
	[ThemePref.Re_Sample]: {
		key: 'resample',
		nameFn: () => 'Re:Sample',
		preview: previewResample
	}
};

export const themeDisplayOrder: ThemePref[] = [
	ThemePref.Default,
	ThemePref.Plain_Dark,
	ThemePref.Plain_Light,
	ThemePref.Aniki,
	ThemePref.otogroove,
	ThemePref.Retro_Voyage,
	ThemePref.SORIMIX,
	ThemePref.Re_Sample
];
