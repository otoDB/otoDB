// See https://svelte.dev/docs/kit/types#app.d.ts

import type { components, Preferences } from '$lib/schema';

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user:
				| ({ csrf: string } & Omit<components['schemas']['UserStatusSchema'], 'prefs'> & {
							prefs: Map<Preferences, number>;
						})
				| null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
	namespace svelteHTML {
		interface HTMLAttributes<T> {
			onoutclick?: () => void;
		}
	}
}

export {};
