/**
 * Tag Work Connection
 */

export const TagWorkConnection = {
	OTOMADWIKI: {
		id: 1,
		name: 'otomad.wiki',
		linkFn: (id: string) => `https://otomad.wiki/tag/${id}`
	},
	OTOMADFANDOM: {
		id: 2,
		name: '音MAD Wiki 2',
		linkFn: (id: string) => `https://otomad.fandom.com/ja/wiki/${id}`
	},
	NICOPEDIA: {
		id: 20,
		name: 'Niconico Encyclopedia',
		linkFn: (id: string) => `https://dic.nicovideo.jp/${id}`
	},
	PIXIV_DICT: {
		id: 21,
		name: 'Pixiv Dictionary',
		linkFn: (id: string) => `https://dic.pixiv.net/a/${id}/`
	},
	WIKIPEDIAEN: {
		id: 22,
		name: 'Wikipedia (en)',
		linkFn: (id: string) => `https://en.wikipedia.org/wiki/${id}`
	},
	NAMUWIKI: {
		id: 23,
		name: 'Namu Wiki',
		linkFn: (id: string) => `https://namu.wiki/w/${id}`
	},
	KNOWYOURMEME: {
		id: 24,
		name: 'Know Your Meme',
		linkFn: (id: string) => `https://knowyourmeme.com/${id}`
	}
} as const;

/**
 * @deprecated
 */
export const resolveTagWorkConnectionNameById = (id: number): keyof typeof TagWorkConnection => {
	return Object.entries(TagWorkConnection).find(
		([_, value]) => value.id === id
	)?.[0] as keyof typeof TagWorkConnection;
};
