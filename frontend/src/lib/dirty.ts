import { enhance } from '$app/forms';
import { m } from '$lib/paraglide/messages';
import type { SubmitFunction } from '@sveltejs/kit';
import type { Attachment } from 'svelte/attachments';

// Locks a button while its handler is in flight to prevent double-clicks.
export const dirtyClick =
	(handler: () => Promise<void>): Attachment<HTMLButtonElement> =>
	(node) => {
		const onclick = async () => {
			if (node.disabled) return;
			node.disabled = true;
			try {
				await handler();
			} finally {
				node.disabled = false;
			}
		};
		node.addEventListener('click', onclick);
		return () => node.removeEventListener('click', onclick);
	};

export const isFormDirty = (f: HTMLFormElement) => f.dataset.dirty && !f.action.includes('search');

type Barrier = {
	forms: HTMLFormElement[];
	reached: ReturnType<typeof Promise.withResolvers<void>>[];
};

export type Control = {
	barrier: { [K in keyof Barrier]?: never };
	priority: number;
};

export const dirtyEnhance = (
	node: HTMLFormElement,
	props?: {
		control?: Control;
		form?: any;
		custom_submit?: SubmitFunction;
	}
) => {
	node.dataset.priority = props?.control?.priority.toString();
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
	});

	return enhance(node, async (input) => {
		const { cancel } = input;
		const dirty_forms = Array.from(document.querySelectorAll('form')).filter(isFormDirty);

		if (props?.control) {
			const first = !Object.hasOwn(props.control.barrier, 'reached');
			if (first) {
				// Check HTML form validation (i.e. min/max, type, etc) before proceeding
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}
				dirty_forms.sort((a, b) => +(a.dataset.priority ?? 0) - +(b.dataset.priority ?? 0));
				// Lock all forms and make locks for each form (resolvers)
				dirty_forms.forEach((f) => {
					f.inert = true;
				});
				(props.control.barrier as unknown as Barrier) = {
					forms: dirty_forms,
					reached: Array(dirty_forms.length)
						.fill(null)
						.map(() => Promise.withResolvers<void>())
				};
			}

			const barrier = props.control.barrier as unknown as Barrier;

			let orchestrator: AsyncGenerator | null = null;
			if (first) {
				// Submit forms in [start, end) sequentially, awaiting each lock.
				// Note that other forms' submission logic is handled in the same function:
				// they enter with first=false and just attach their own response handler.
				const my_id = barrier.forms!.indexOf(node);
				async function* make_orchestrator() {
					for (let i = 0; i < barrier.forms.length; i++) {
						barrier.forms![i].requestSubmit();
						try {
							if (i == my_id) yield;
							await barrier.reached![i].promise;
						} catch {
							barrier.forms.forEach((f) => {
								f.inert = false;
							});
							(barrier as Partial<Barrier>).forms = undefined;
							(barrier as Partial<Barrier>).reached = undefined;
							return false;
						}
					}
					return true;
				}
				orchestrator = make_orchestrator();
			}

			const result = await orchestrator?.next();
			if (!result || !result.done) {
				// We must be dirty. Try to submit self and continue if applicable.
				const my_id = barrier.forms!.indexOf(node);
				const { resolve, reject } = barrier.reached![my_id];
				let handler: null | Awaited<ReturnType<SubmitFunction>> = null;
				if (props?.custom_submit) {
					try {
						handler = await props.custom_submit(input);
						resolve();
						delete node.dataset.dirty;
					} catch {
						reject();
						cancel();
						return;
					}
				}
				return async (output) => {
					let updated = false;
					const update: typeof output.update = async (options) => {
						updated = true;
						if (output.result.type === 'success' || output.result.type === 'redirect') {
							resolve();
							delete node.dataset.dirty;
							// Only do update if we are orchestrating
							void ((await orchestrator?.next()) || (await output.update(options)));
						} else {
							reject();
							await output.update(options);
						}
					};
					if (handler) await handler({ ...output, update });
					if (!updated) await update();
				};
			}
		} else {
			// No barrier, just a simple double-submit guard and dirty check.
			// Cancel the submit if dirty and not confirmed
			if (dirty_forms.some((f) => f !== node) && !confirm(m.active_lime_panther_buzz())) {
				cancel();
				return;
			}

			node.inert = true;

			let handler: null | Awaited<ReturnType<SubmitFunction>> = null;
			let cancelled = false;
			if (props?.custom_submit) {
				try {
					handler = await props.custom_submit({
						...input,
						cancel: () => {
							cancelled = true;
							cancel();
						}
					});
					delete node.dataset.dirty;
				} catch {
					// caller handles its own errors
				}
			}
			if (cancelled) {
				cancel();
				node.inert = false;
				return;
			}

			return async (output) => {
				let updated = false;
				const update: typeof output.update = async (options) => {
					updated = true;
					node.inert = false;
					if (output.result.type === 'success' || output.result.type === 'redirect')
						delete node.dataset.dirty;
					await output.update(options);
				};
				if (handler) await handler({ ...output, update });
				if (!updated) await update();
			};
		}
	});
};
