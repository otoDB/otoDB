/**
 * Media Connection
 */

export const MediaConnection = {
	ANIKORE: {
		id: 1,
		name: 'AniKore',
		linkFn: (id: string) => `https://www.anikore.jp/anime/${id}/`
	},
	BANGUMI: {
		id: 2,
		name: 'Bangumi',
		linkFn: (id: string) => `https://bangumi.tv/subject/${id}`
	},
	ANIDB: {
		id: 3,
		name: 'AniDB',
		linkFn: (id: string) => `https://anidb.net/anime/${id}`
	},
	MYANIMELIST: {
		id: 4,
		name: 'MyAnimeList',
		linkFn: (id: string) => `https://myanimelist.net/anime/${id}`
	},
	ANILIST: {
		id: 5,
		name: 'AniList',
		linkFn: (id: string) => `https://anilist.co/anime/${id}`
	},
	KITSU: {
		id: 6,
		name: 'Kitsu',
		linkFn: (id: string) => `https://kitsu.io/anime/${id}`
	},
	ANIMEPLANET: {
		id: 7,
		name: 'Anime-Planet',
		linkFn: (id: string) => `https://www.anime-planet.com/anime/${id}`
	},
	IMDB: {
		id: 20,
		name: 'IMDb',
		linkFn: (id: string) => `https://www.imdb.com/title/${id}/`
	},
	LETTERBOXD: {
		id: 21,
		name: 'Letterboxd',
		linkFn: (id: string) => `https://letterboxd.com/film/${id}/`
	},
	VNDB: {
		id: 40,
		name: 'vndb',
		linkFn: (id: string) => `https://vndb.org/${id}`
	},
	EROGAMESCAPE: {
		id: 41,
		name: 'ErogameScape',
		linkFn: (id: string) =>
			`https://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/game.php?game=${id}`
	},
	VGMDB: {
		id: 50,
		name: 'VGMdb',
		linkFn: (id: string) => `https://vgmdb.net/product/${id}`
	}
} as const;

/**
 * @deprecated
 */
export const resolveMediaConnectionNameById = (id: number): keyof typeof MediaConnection => {
	return Object.entries(MediaConnection).find(
		([_, value]) => value.id === id
	)?.[0] as keyof typeof MediaConnection;
};
