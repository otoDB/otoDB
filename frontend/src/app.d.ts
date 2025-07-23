// See https://svelte.dev/docs/kit/types#app.d.ts

import type { components } from '$lib/schema';

// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: {
				csrf: string;
				user_id: number;
				username: string;
				level: int;
				prefs: components['schemas']['UserPreferencesSchema']?;
			};
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
	namespace svelteHTML {
		interface HTMLAttributes<T> {
			onOutclick?: () => void;
		}
	}
}

export {};
