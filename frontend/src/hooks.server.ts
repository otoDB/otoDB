import type { Handle } from '@sveltejs/kit';
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
