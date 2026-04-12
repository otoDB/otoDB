export const languages = {
	en: {
		id: 1,
		name: 'English'
	},
	ja: {
		id: 2,
		name: '日本語'
	},
	'zh-cn': {
		id: 3,
		name: '简体中文'
	},
	ko: {
		id: 4,
		name: '한국어'
	}
} as const satisfies Record<string, { id: number; name: string }>;

/**
 * @deprecated
 */
export function resolveLanguageKeyById(id: number): keyof typeof languages {
	return Object.entries(languages).find(
		([_, value]) => value.id === id
	)?.[0] as keyof typeof languages;
}

export const getLanguageId = (lang: keyof typeof languages): number => languages[lang].id;

export const isSVO = (lang: keyof typeof languages) => {
	switch (lang) {
		case 'en':
		case 'zh-cn':
			return true;
		default:
			return false;
	}
};
export const isSOV = (lang: keyof typeof languages) => {
	switch (lang) {
		case 'ko':
		case 'ja':
			return true;
		default:
			return false;
	}
};
