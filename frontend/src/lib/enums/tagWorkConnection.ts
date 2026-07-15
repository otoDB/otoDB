import { TagWorkConnectionTypes } from '$lib/schema';

export const TagWorkConnectionMap: Record<
	TagWorkConnectionTypes,
	{ name: string; linkFn: (id: string) => string }
> = {
	[TagWorkConnectionTypes.otomad_wiki]: {
		name: 'otomad.wiki',
		linkFn: (id: string) => `https://otomad.wiki/tag/${id}`
	},
	[TagWorkConnectionTypes.Otomad_Wiki_2]: {
		name: '音MAD Wiki 2',
		linkFn: (id: string) => `https://otomad.fandom.com/ja/wiki/${id}`
	},
	[TagWorkConnectionTypes.Niconico_Encyclopedia]: {
		name: 'Niconico Encyclopedia',
		linkFn: (id: string) => `https://dic.nicovideo.jp/${id}`
	},
	[TagWorkConnectionTypes.Pixiv_Dictionary]: {
		name: 'Pixiv Dictionary',
		linkFn: (id: string) => `https://dic.pixiv.net/a/${id}/`
	},
	[TagWorkConnectionTypes.Wikipedia]: {
		name: 'Wikipedia (en)',
		linkFn: (id: string) => `https://en.wikipedia.org/wiki/${id}`
	},
	[TagWorkConnectionTypes.Namu_Wiki]: {
		name: 'Namu Wiki',
		linkFn: (id: string) => `https://namu.wiki/w/${id}`
	},
	[TagWorkConnectionTypes.Know_Your_Meme]: {
		name: 'Know Your Meme',
		linkFn: (id: string) => `https://knowyourmeme.com/${id}`
	}
};
