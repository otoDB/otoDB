/**
 * Song Connection
 */

export const SongConnection = {
	VGMDB: {
		id: 0,
		name: 'VGMdb',
		linkFn: (id: string) => `https://vgmdb.net/album/${id}`
	},
	VOCADB: {
		id: 1,
		name: 'VocaDB',
		linkFn: (id: string) => `https://vocadb.net/S/${id}`
	},
	DISCOGS: {
		id: 2,
		name: 'Discogs',
		linkFn: (id: string) => `https://www.discogs.com/master/${id}`
	},
	MUSICBRAINZ: {
		id: 3,
		name: 'MusicBrainz',
		linkFn: (id: string) => `https://musicbrainz.org/recording/${id}`
	},
	RATEYOURMUSIC: {
		id: 4,
		name: 'Rate Your Music',
		linkFn: (id: string) => `https://rateyourmusic.com/song/${id}/`
	},
	DOJINMUSICINFO: {
		id: 5,
		name: '同人音楽info',
		linkFn: (id: string) => `https://www.dojin-music.info/song/${id}`
	},
	TOUHOUDB: {
		id: 6,
		name: 'TouhouDB',
		linkFn: (id: string) => `https://touhoudb.com/S/${id}`
	},
	REMYWIKI: {
		id: 20,
		name: 'RemyWiki',
		linkFn: (id: string) => `https://remywiki.com/${id}`
	},
	SILENTBLUE: {
		id: 21,
		name: 'Silent Blue',
		linkFn: (id: string) => `https://silentblue.remywiki.com/${id}`
	},
	ZENIUS: {
		id: 22,
		name: 'Zenius -I- vanisher.com',
		linkFn: (id: string) => `https://zenius-i-vanisher.com/v5.2/songdb.php?songid=${id}`
	},
	NNDMEDLEYWIKI: {
		id: 30,
		name: 'NND Medley Wiki',
		linkFn: (id: string) => `https://medley.bepis.io/wiki/${id}`
	},
	MODARCHIVE: {
		id: 40,
		name: 'The Mod Archive',
		linkFn: (id: string) =>
			`https://modarchive.org/index.php?request=view_by_moduleid&query=${id}`
	}
} as const;

/**
 * @deprecated
 */
export const resolveSongConnectionNameById = (id: number): keyof typeof SongConnection => {
	return Object.entries(SongConnection).find(
		([_, value]) => value.id === id
	)?.[0] as keyof typeof SongConnection;
};
