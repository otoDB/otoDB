// See https://svelte.dev/docs/kit/types#app.d.ts

import type { components } from '$lib/schema';

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: ({ csrf: string } & components['schemas']['UserStatusSchema']) | null;
		}
		// interface PageData {}
		interface PageState {
			// Post targeted by an in-thread t{thread}.{num} reference click (shallow routing)
			// This is so ThreadView can highlight the post and scroll to it on navigation, including back/forward
			postNum?: string;
		}
		// interface Platform {}
	}
	namespace svelteHTML {
		interface HTMLAttributes<T> {
			onoutclick?: () => void;
		}
	}
}

export {};
