import type { SubmitFunction } from '@sveltejs/kit';

export function submission_state(): {
	readonly is_submitting: boolean;
	readonly enhance: SubmitFunction;
} {
	let is_submitting = $state(false);

	const enhance: SubmitFunction = ({ cancel }) => {
		if (is_submitting) {
			cancel();
			return;
		}
		is_submitting = true;

		return async ({ update }) => {
			try {
				await update();
			} finally {
				is_submitting = false;
			}
		};
	};

	return {
		get is_submitting() {
			return is_submitting;
		},
		get enhance() {
			return enhance;
		}
	};
}
