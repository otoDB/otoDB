import * as Sentry from '@sentry/sveltekit';
import type { Handle, HandleFetch, HandleServerError } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { env } from '$env/dynamic/private';
import client from '$lib/api.server';
import { paraglideMiddleware } from '$lib/paraglide/server';
import { defineCustomServerStrategy } from '$lib/paraglide/runtime';
import { getRequestEvent } from '$app/server';
import { resolveLanguageKeyById } from '$lib/enums/language';

if (env.OTODB_FRONTEND_SENTRY_DSN) {
	Sentry.init({
		dsn: env.OTODB_FRONTEND_SENTRY_DSN,
		sendDefaultPii: false,
		enableLogs: true,
		tracesSampleRate: parseFloat(env.OTODB_FRONTEND_SENTRY_TRACES_SAMPLE_RATE ?? '0.1'),
		release: process.env.PUBLIC_OTODB_HASH || undefined
	});
}

defineCustomServerStrategy('custom-userPreference', {
	getLocale: () => {
		const lang = getRequestEvent().locals.user?.prefs.LANGUAGE;
		return lang ? resolveLanguageKeyById(lang) : undefined;
	}
});

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

export const handle: Handle = sequence(
	Sentry.sentryHandle(),
	handleAuth,
	handleContentLength,
	handleParaglide
);

export const handleError: HandleServerError = Sentry.handleErrorWithSentry(({ error, event }) => {
	console.error('Server error:', error, event.url.pathname);
});

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
	if (env.INTERNAL_API_ENDPOINT && request.url.startsWith(env.INTERNAL_API_ENDPOINT)) {
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
