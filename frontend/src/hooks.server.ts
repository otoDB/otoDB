import type { Handle, HandleFetch } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';
import { i18n } from '$lib/i18n';
const handleParaglide: Handle = i18n.handle();

const handleContentLength: Handle = async ({ event, resolve }) => {
  return resolve(event, {
    filterSerializedResponseHeaders(name) {
      // SvelteKit doesn't serialize any headers on server-side fetches by default but openapi-fetch uses this header for empty responses.
      return name === "content-length";
    },
  });
};

export const handle: Handle = sequence(handleContentLength, handleParaglide);

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
  if (request.url.startsWith('http://backend:8000')) {
    const cookies = event.request.headers.get('cookie');
    if (cookies)
      request.headers.set('cookie', cookies);

    const csrf = event.cookies.get('csrftoken');
    if (csrf && cookies?.includes('csrftoken=' + csrf))
      request.headers.set('X-CSRFToken', csrf);
  }

  return fetch(request);
};
