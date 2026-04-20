import type { Handle, HandleFetch } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { env } from '$env/dynamic/public';
import client from '$lib/api';
import { paraglideMiddleware } from '$lib/paraglide/server';
import { themes } from '$lib/themes/themes';
import { ThemePref } from '$lib/schema';

const handleParaglide: Handle = ({ event, resolve }) =>
	paraglideMiddleware(event.request, ({ request: localizedRequest, locale }) => {
		event.request = localizedRequest;
		return resolve(event, {
			transformPageChunk: ({ html }) => html.replace('%paraglide.lang%', locale)
		});
	});

const handleAuth: Handle = async ({ event, resolve }) => {
	const session = event.cookies.get('sessionid');
	const csrf = event.cookies.get('csrftoken');

	if (session && csrf) {
		const status = await client.GET('/api/auth/status', { fetch: event.fetch });

		if (status.data) event.locals.user = { csrf: csrf, ...status.data };
		else event.locals.user = null;
	}

	return resolve(event);
};

const handleContentLength: Handle = async ({ event, resolve }) => {
	return resolve(event, {
		filterSerializedResponseHeaders(name) {
			// SvelteKit doesn't serialize any headers on server-side fetches by default but openapi-fetch uses this header for empty responses.
			return name === 'content-length';
		}
	});
};

const handleTheme: Handle = async ({ event, resolve }) => {
	// login-user preference
	const userTheme = event.locals.user?.prefs?.theme;
	if (userTheme)
		return resolve(event, {
			transformPageChunk: ({ html }) => html.replace('%otodb.theme%', themes[userTheme].key)
		});

	// cookie preference
	const cookieTheme = event.cookies.get('theme');
	if (cookieTheme) {
		const parsed = parseInt(cookieTheme);
		if (!isNaN(parsed) && Object.values(ThemePref).includes(parsed))
			return resolve(event, {
				transformPageChunk: ({ html }) =>
					html.replace('%otodb.theme%', themes[parsed as ThemePref].key)
			});
	}

	// fallback
	event.cookies.set('theme', ThemePref.Default.toString(), {
		path: '/',
		maxAge: 60 * 60 * 24 * 365
	});
	return resolve(event, {
		transformPageChunk: ({ html }) =>
			html.replace('%otodb.theme%', themes[ThemePref.Default].key)
	});
};

export const handle: Handle = sequence(
	handleAuth,
	handleContentLength,
	handleParaglide,
	handleTheme
);

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
	if (
		env.PUBLIC_BACKEND_URL_INTERNAL &&
		request.url.startsWith(env.PUBLIC_BACKEND_URL_INTERNAL)
	) {
		const cookies = event.request.headers.get('cookie');
		if (cookies) request.headers.set('cookie', cookies);

		const csrf = event.cookies.get('csrftoken');
		if (csrf && cookies?.includes('csrftoken=' + csrf))
			request.headers.set('X-CSRFToken', csrf);

		for (const header of [
			'X-Forwarded-For',
			'X-Forwarded-Proto',
			'X-Forwarded-Host',
			'User-Agent'
		]) {
			const value = event.request.headers.get(header);
			if (value) request.headers.set(header, value);
		}
	}

	return fetch(request);
};
