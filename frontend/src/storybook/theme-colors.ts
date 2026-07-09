// Colors for every theme, read directly from `../themes.json` — the same JSON that the
// `postcss-map` plugin (see postcss.config.js) expands into `../themes.css`'s custom
// properties, so this can never drift from the app's actual colors.
//
// `default` follows the OS `prefers-color-scheme` and is intentionally omitted — its colors
// vary by machine.
import themesJson from '../themes.json';

export interface ThemeColors {
	name: string;
	bgPrimary: string;
	bgFaint: string;
	bgFainter: string;
	contentPrimary: string;
	contentFaint: string;
	contentFainter: string;
}

const LABELS = {
	'plain-dark': 'Plain Dark',
	'plain-light': 'Plain Light',
	'aniki': 'Aniki',
	'otogroove': 'otogroove',
	'retro-voyage': 'Retro Voyage',
	'sorimix': 'SORIMIX',
	'resample': 'Re:Sample'
} as const satisfies Partial<Record<keyof typeof themesJson, string>>;

export const themeColors: ThemeColors[] = (Object.keys(LABELS) as (keyof typeof LABELS)[]).map(
	(key) => ({ name: LABELS[key], ...themesJson[key].colors }) as ThemeColors
);
