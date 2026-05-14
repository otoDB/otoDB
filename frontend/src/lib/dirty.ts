import { enhance } from '$app/forms';
import { m } from '$lib/paraglide/messages';
import type { SubmitFunction } from '@sveltejs/kit';

export const isFormDirty = (f: HTMLFormElement) => f.dataset.dirty && !f.action.includes('search');

export type Barrier = {
	forms: HTMLFormElement[];
	reached: ReturnType<typeof Promise.withResolvers<void>>[];
};

const dirty_failure = (dirty_forms: HTMLFormElement[], barrier: Partial<Barrier>) => {
	dirty_forms.forEach((f) => {
		f.inert = false;
	});
	barrier.forms = undefined;
	barrier.reached = undefined;
};

export const dirtyEnhance = (
	node: HTMLFormElement,
	props:
		| {
				barrier?: Partial<Barrier>;
				priority?: number;
				form?: any;
				submit?: () => Promise<void>;
		  }
		| SubmitFunction
		| undefined = undefined
) => {
	const submit = typeof props === 'function' ? props : undefined;
	if (typeof props === 'function') props = undefined;

	node.dataset.priority = props?.priority?.toString();
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
	});

	return enhance(node, async (input) => {
		const { cancel } = input;
		const dirty_forms = Array.from(document.querySelectorAll('form')).filter(isFormDirty);
		const me_dirty = node.dataset.dirty;

		if (props?.barrier) {
			const barrier = props.barrier;
			// If we are the first form to reach the barrier (i.e. where the submit
			// event came from):
			const first = !barrier.reached?.length;
			if (first) {
				// Check HTML form validation (i.e. min/max, type, etc) before proceeding
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}

				// Lock all forms and make locks for each form (resolvers)
				dirty_forms.forEach((f) => {
					f.inert = true;
				});
				barrier.forms = dirty_forms.toSorted(
					(a, b) => +(a.dataset.priority ?? 0) - +(b.dataset.priority ?? 0)
				);
				barrier.reached = Array(barrier.forms.length)
					.fill(null)
					.map(() => Promise.withResolvers<void>());
			}

			// Submit forms in [start, end) sequentially, awaiting each lock.
			// Note that other forms' submission logic is handled in the same function:
			// they enter with first=false and just attach their own response handler.
			const orchestrate = async (start: number, end: number) => {
				for (let i = start; i < end; i++) {
					barrier.forms![i].requestSubmit();
					try {
						await barrier.reached![i].promise;
					} catch {
						dirty_failure(dirty_forms, barrier);
						return false;
					}
				}
				return true;
			};

			// Start orchestration of form submissions from the handler where the
			// submit event came from (i.e. first form to reach the barrier)
			if (me_dirty) {
				// If we are dirty, then we need to include ourselves in the orchestration.
				const my_id = barrier.forms!.indexOf(node);
				// Try submitting all forms with higher priority.
				if (first && !(await orchestrate(0, my_id))) {
					cancel();
					return;
				}
				const { resolve, reject } = barrier.reached![my_id];

				// Try to submit self. On success, resolve our own lock and proceed
				// to try submitting forms with lower priority.
				if (props?.submit) {
					// Caller drives its own POST; skip the action submission.
					cancel();
					try {
						await props.submit();
					} catch {
						reject();
						return;
					}
					resolve();
					delete node.dataset.dirty;
					if (first) await orchestrate(my_id + 1, barrier.forms!.length);
				} else
					return async ({ update, result }) => {
						if (result.type === 'success' || result.type === 'redirect') {
							resolve();
							delete node.dataset.dirty;
							if (first) {
								await orchestrate(my_id + 1, barrier.forms!.length);
								await update();
							}
						} else {
							reject();
							if (props.form !== undefined && result) props.form = result;
						}
					};
			} else {
				// If we are not dirty: just proceed to try submitting forms in order
				await orchestrate(0, barrier.forms!.length);
			}
		} else {
			// No barrier, just a simple double-submit guard and dirty check.
			// Double-submit guard: form is already in flight
			if (node.inert) {
				cancel();
				return;
			}

			// If there are any dirty forms (including self) and the user doesn't confirm, cancel the submit
			if (dirty_forms.some((f) => f !== node) && !confirm(m.active_lime_panther_buzz())) {
				cancel();
				return;
			}

			node.inert = true;

			// Caller drives its own POST; skip the action submission.
			if (props?.submit) {
				cancel();
				try {
					await props.submit();
				} catch {
					// caller handles its own errors
				} finally {
					node.inert = false;
				}
				return;
			}

			// Wrap `cancel` so we can detect if the caller's submit handler cancels
			// and roll back the lock
			let cancelled = false;
			const original_cancel = input.cancel;
			input.cancel = () => {
				cancelled = true;
				original_cancel();
			};

			let handler: Awaited<ReturnType<SubmitFunction>>;
			try {
				handler = await submit?.(input);
			} catch (e) {
				node.inert = false;
				throw e;
			}

			if (cancelled) {
				node.inert = false;
				return;
			}

			// Release the lock once the request finishes
			return async (output) => {
				try {
					if (handler) await handler(output);
					else await output.update();
				} finally {
					node.inert = false;
				}
			};
		}
	});
};
