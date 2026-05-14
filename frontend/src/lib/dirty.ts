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
		| ({
				barrier: Partial<Barrier>;
				priority: number;
		  } & { form?: any; manual_post?: { p: ReturnType<typeof Promise.withResolvers<void>> } })
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

		if (props?.manual_post) cancel();

		if (props?.barrier) {
			// If we are the first form to reach the barrier (i.e. where the submit
			// event came from):
			const first = !props?.barrier.reached?.length;
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
				props.barrier.forms = dirty_forms.toSorted(
					(a, b) => +(a.dataset.priority ?? 0) - +(b.dataset.priority ?? 0)
				);
				props.barrier.reached = Array(props.barrier.forms.length)
					.fill(null)
					.map(() => Promise.withResolvers<void>());
			}
			// Start orchestration of form submissions from the handler where the
			// submit event came from (i.e. first form to reach the barrier)
			if (me_dirty) {
				// If we are dirty, then we need to include ourselves in the orchestration.
				const my_id = props.barrier.forms!.indexOf(node);
				if (first)
					// Try submitting all forms with higher priority. Note that other
					// forms' submission logic is handled in the same function! Those
					// forms being orchestrated by the first form to reach the barrier
					// will not try to submit other forms.
					for (let i = 0; i < my_id; i++) {
						props.barrier.forms![i].requestSubmit();
						try {
							await props.barrier.reached![i].promise;
						} catch {
							dirty_failure(dirty_forms, props.barrier);
							props?.manual_post?.p.reject();
							cancel();
							return;
						}
					}
				const { resolve, reject } = props.barrier.reached![my_id];

				// Try to submit self. If successful (in on_success), resolve our own
				// lock and proceed to try submitting forms with lower priority
				const on_success = async () => {
					resolve();
					delete node.dataset.dirty;
					if (first) {
						for (let i = my_id + 1; i < props.barrier.reached!.length; i++) {
							props.barrier.forms![i].requestSubmit();
							try {
								await props.barrier.reached![i].promise;
							} catch {
								dirty_failure(dirty_forms, props.barrier);
								return;
							}
						}
					}
				};

				if (props?.manual_post) {
					props?.manual_post?.p.resolve();
					on_success();
				} else
					return async ({ update, result }) => {
						if (result.type === 'success' || result.type === 'redirect') {
							on_success();
							if (first) await update();
						} else {
							reject();
							if (props.form !== undefined && result) props.form = result;
						}
					};
			} else {
				// If we are not dirty: just proceed to try submitting forms in order
				props.manual_post?.p.resolve();
				for (let i = 0; i < props.barrier.forms!.length; i++) {
					props.barrier.forms![i].requestSubmit();
					try {
						await props.barrier.reached![i].promise;
					} catch {
						dirty_failure(dirty_forms, props.barrier);
						return;
					}
				}
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
				props?.manual_post?.p.reject();
				return;
			}

			node.inert = true;

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
		props?.manual_post?.p.resolve();
	});
};
