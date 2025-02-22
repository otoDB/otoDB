import type { Handle, HandleFetch } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { i18n } from '$lib/i18n';
import { PUBLIC_BACKEND_URL_INTERNAL } from '$env/static/public';
import client from '$lib/api';
const handleParaglide: Handle = i18n.handle();

const handleAuth: Handle = async ({event, resolve}) => {
  const session = event.cookies.get('sessionid'),
  csrf = event.cookies.get('csrftoken');
  if (session && csrf) {
    const status = await client.GET('/api/auth/status', { fetch: event.fetch });
    if (status.data)
      event.locals.user = { csrf: csrf, ...status.data };
  }

  return resolve(event);
}

const handleContentLength: Handle = async ({ event, resolve }) => {
  return resolve(event, {
    filterSerializedResponseHeaders(name) {
      // SvelteKit doesn't serialize any headers on server-side fetches by default but openapi-fetch uses this header for empty responses.
      return name === "content-length";
    },
  });
};

export const handle: Handle = sequence(handleAuth, handleContentLength, handleParaglide);

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
  if (request.url.startsWith(PUBLIC_BACKEND_URL_INTERNAL)) {
    const cookies = event.request.headers.get('cookie');
    if (cookies)
      request.headers.set('cookie', cookies);

    const csrf = event.cookies.get('csrftoken');
    if (csrf && cookies?.includes('csrftoken=' + csrf))
      request.headers.set('X-CSRFToken', csrf);
  }

  return fetch(request);
};
