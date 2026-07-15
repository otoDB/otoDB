import { describe, expect, it } from 'bun:test';
import { extractUrl } from './extractUrl';

describe('extractUrl', () => {
	describe('Niconico', () => {
		it('returns Niconico for a www.nicovideo.jp user page', () => {
			expect(extractUrl('https://www.nicovideo.jp/user/12345/')).toBe('Niconico');
		});
	});

	describe('Niconico Encyclopedia', () => {
		it('returns Niconico Encyclopedia for a dic.nicovideo.jp page', () => {
			expect(extractUrl('https://dic.nicovideo.jp/a/foo')).toBe('Niconico Encyclopedia');
		});
	});

	describe('YouTube', () => {
		it('returns YouTube for a youtube.com URL', () => {
			expect(extractUrl('https://www.youtube.com/@example')).toBe('YouTube');
		});
	});

	describe('Twitter', () => {
		it('returns Twitter for a twitter.com URL', () => {
			expect(extractUrl('https://twitter.com/example/')).toBe('Twitter');
		});
	});

	describe('VGMdb', () => {
		it('returns VGMdb for a vgmdb.net URL', () => {
			expect(extractUrl('https://vgmdb.net/album/12345')).toBe('VGMdb');
		});
	});

	describe('unmatched input', () => {
		it('returns null for an unrecognized host', () => {
			expect(extractUrl('https://example.com/foo')).toBeNull();
		});

		it('returns null for an invalid URL string', () => {
			expect(extractUrl('not a url')).toBeNull();
		});

		it('returns null for an empty string', () => {
			expect(extractUrl('')).toBeNull();
		});
	});
});
