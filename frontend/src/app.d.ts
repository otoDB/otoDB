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
