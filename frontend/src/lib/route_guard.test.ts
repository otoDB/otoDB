import { describe, expect, it, mock } from 'bun:test';

// Mock paraglide messages before importing UserLevel
mock.module('$lib/paraglide/messages.js', () => ({
	heroic_busy_shrimp_lend: () => 'ANONYMOUS',
	fancy_formal_falcon_quell: () => 'RESTRICTED',
	drab_alive_midge_edit: () => 'MEMBER',
	tasty_spry_firefox_fall: () => 'EDITOR',
	silly_blue_felix_amuse: () => 'ADMIN',
	tangy_formal_lionfish_tap: () => 'OWNER'
}));

// Mock @sveltejs/kit redirect so it throws a detectable object instead of a Response
mock.module('@sveltejs/kit', () => ({
	redirect: (status: number, location: string) => {
		throw { _isRedirect: true, status, location };
	}
}));

const { userLevelGuard } = await import('./route_guard');

const makeUser = (level: number) => ({
	csrf: 'test-csrf',
	user_id: 1,
	username: 'testuser',
	level,
	notifs_count: 0,
	prefs: null
});

describe('userLevelGuard', () => {
	it('redirects to /login when user is null', () => {
		expect(() => userLevelGuard(null, 'MEMBER')).toThrow();
	});

	it('redirects when user level is below required level', () => {
		// RESTRICTED (id=10) does not meet MEMBER (id=20)
		expect(() => userLevelGuard(makeUser(10), 'MEMBER')).toThrow();
	});

	it('redirects when user level is anonymous and MEMBER is required', () => {
		// ANONYMOUS (id=0) does not meet MEMBER (id=20)
		expect(() => userLevelGuard(makeUser(0), 'MEMBER')).toThrow();
	});

	it('does NOT redirect when user exactly meets required level', () => {
		// MEMBER (id=20) meets MEMBER (id=20)
		expect(userLevelGuard(makeUser(20), 'MEMBER')).toBe(true);
	});

	it('does NOT redirect when user exceeds required level', () => {
		// ADMIN (id=50) exceeds MEMBER (id=20)
		expect(userLevelGuard(makeUser(50), 'MEMBER')).toBe(true);
	});

	it('redirects to custom destination', () => {
		let redirectLocation: string | undefined;
		try {
			userLevelGuard(null, 'MEMBER', null, '/unauthorized');
		} catch (e: unknown) {
			redirectLocation = (e as { location: string }).location;
		}
		expect(redirectLocation).toBe('/unauthorized');
	});

	it('redirects to /login with ?from= when from path is provided', () => {
		let redirectLocation: string | undefined;
		try {
			userLevelGuard(null, 'MEMBER', '/protected-page');
		} catch (e: unknown) {
			redirectLocation = (e as { location: string }).location;
		}
		expect(redirectLocation).toBe('/login?from=/protected-page');
	});
});
