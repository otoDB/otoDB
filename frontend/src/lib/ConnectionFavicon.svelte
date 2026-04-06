<script lang="ts">
	import faviconAniDB from './connection_favicon/AniDB.png';
	import faviconAniKore from './connection_favicon/AniKore.png';
	import faviconAniList from './connection_favicon/AniList.png';
	import faviconAnimePlanet from './connection_favicon/Anime-Planet.png';
	import faviconBangumi from './connection_favicon/Bangumi.png';
	import faviconBilibili from './connection_favicon/Bilibili.png';
	import faviconBluesky from './connection_favicon/Bluesky.png';
	import faviconDiscogs from './connection_favicon/Discogs.png';
	import faviconErogameScape from './connection_favicon/ErogameScape.png';
	import faviconIMDb from './connection_favicon/IMDb.png';
	import faviconKitsu from './connection_favicon/Kitsu.png';
	import faviconKnowYourMeme from './connection_favicon/Know Your Meme.png';
	import faviconLetterboxd from './connection_favicon/Letterboxd.png';
	import faviconModArchive from './connection_favicon/The Mod Archive.png';
	import faviconMusicBrainz from './connection_favicon/MusicBrainz.png';
	import faviconMyAnimeList from './connection_favicon/MyAnimeList.png';
	import faviconNNDMedleyWiki from './connection_favicon/NND Medley Wiki.png';
	import faviconNamuWiki from './connection_favicon/Namu Wiki.png';
	import faviconNiconicoEncyclopedia from './connection_favicon/Niconico Encyclopedia.png';
	import faviconNiconico from './connection_favicon/Niconico.png';
	import faviconPixivDictionary from './connection_favicon/Pixiv Dictionary.png';
	import faviconRateYourMusic from './connection_favicon/Rate Your Music.png';
	import faviconRemyWiki from './connection_favicon/RemyWiki.png';
	import faviconSilentBlue from './connection_favicon/Silent Blue.png';
	import faviconTouhouDB from './connection_favicon/TouhouDB.png';
	import faviconTwitter from './connection_favicon/Twitter.png';
	import faviconVGMdb from './connection_favicon/VGMdb.png';
	import faviconVocaDB from './connection_favicon/VocaDB.png';
	import faviconWebsite from './connection_favicon/Website.png';
	import faviconWikipediaEn from './connection_favicon/Wikipedia (en).png';
	import faviconYouTube from './connection_favicon/YouTube.png';
	import faviconZenius from './connection_favicon/Zenius -I- vanisher.com.png';
	import faviconOtomadWiki from './connection_favicon/otomad.wiki.png';
	import faviconVndb from './connection_favicon/vndb.png';
	import faviconDoujinMusicInfo from './connection_favicon/同人音楽info.png';
	import faviconOtomadWiki2 from './connection_favicon/音MAD Wiki 2.png';
	import faviconSoundcloud from './connection_favicon/Soundcloud.png';

	const img = (
		type: string // TODO: use `keyof typeof ProfileConnection`
	) => {
		switch (type) {
			case 'AniDB':
				return faviconAniDB;
			case 'AniKore':
				return faviconAniKore;
			case 'AniList':
				return faviconAniList;
			case 'Anime-Planet':
				return faviconAnimePlanet;
			case 'Bangumi':
				return faviconBangumi;
			case 'Bilibili':
				return faviconBilibili;
			case 'Bluesky':
				return faviconBluesky;
			case 'Discogs':
				return faviconDiscogs;
			case 'ErogameScape':
				return faviconErogameScape;
			case 'IMDb':
				return faviconIMDb;
			case 'Kitsu':
				return faviconKitsu;
			case 'Know Your Meme':
				return faviconKnowYourMeme;
			case 'Letterboxd':
				return faviconLetterboxd;
			case 'The Mod Archive':
				return faviconModArchive;
			case 'MusicBrainz':
				return faviconMusicBrainz;
			case 'MyAnimeList':
				return faviconMyAnimeList;
			case 'NND Medley Wiki':
				return faviconNNDMedleyWiki;
			case 'Namu Wiki':
				return faviconNamuWiki;
			case 'Niconico Encyclopedia':
				return faviconNiconicoEncyclopedia;
			case 'Niconico':
				return faviconNiconico;
			case 'Pixiv Dictionary':
				return faviconPixivDictionary;
			case 'Rate Your Music':
				return faviconRateYourMusic;
			case 'RemyWiki':
				return faviconRemyWiki;
			case 'Silent Blue':
				return faviconSilentBlue;
			case 'Soundcloud':
				return faviconSoundcloud;
			case 'TouhouDB':
				return faviconTouhouDB;
			case 'Twitter':
				return faviconTwitter;
			case 'VGMdb':
				return faviconVGMdb;
			case 'VocaDB':
				return faviconVocaDB;
			case 'Wikipedia (en)':
				return faviconWikipediaEn;
			case 'YouTube':
				return faviconYouTube;
			case 'Zenius -I- vanisher.com':
				return faviconZenius;
			case 'otomad.wiki':
				return faviconOtomadWiki;
			case 'vndb':
				return faviconVndb;
			case '同人音楽info':
				return faviconDoujinMusicInfo;
			case '音MAD Wiki 2':
				return faviconOtomadWiki2;
			default:
				return faviconWebsite;
		}
	};

	let { type, ...props }: { type: string; class?: string } = $props();
</script>

<img alt={type} src={img(type)} class={[props.class]} />
