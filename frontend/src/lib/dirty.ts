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

type Orchestrator = AsyncGenerator<void, boolean, boolean>;
type Barrier = {
	orchestrator: Orchestrator;
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
			let orchestrating_lock: Promise<void> | null = null;
			if (first) {
				// Check HTML form validation before proceeding
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}
				dirty_forms.sort((a, b) => +(a.dataset.priority ?? 0) - +(b.dataset.priority ?? 0));
				// Lock all forms and make locks for each form (resolvers)
				dirty_forms.forEach((f) => {
					f.inert = true;
				});

				// Submit forms in [start, end) sequentially, awaiting each lock.
				// Note that other forms' submission logic is handled in the same function:
				// they enter with first=false and just attach their own response handler.
				let resolve_orchestrator: null | ReturnType<typeof Promise.withResolvers<void>>['resolve'] =
					null;
				if (node.dataset.dirty)
					({ promise: orchestrating_lock, resolve: resolve_orchestrator } =
						Promise.withResolvers<void>());
				const my_id = dirty_forms.indexOf(node);
				async function* make_orchestrator(): Orchestrator {
					for (let i = 0; i < dirty_forms.length; i++) {
						if (i !== my_id) dirty_forms![i].requestSubmit();
						else void (resolve_orchestrator && resolve_orchestrator());
						if (!(yield)) {
							dirty_forms.forEach((f) => {
								f.inert = false;
							});
							(props?.control?.barrier as Partial<Barrier>).orchestrator = undefined;
							return false;
						}
					}
					return true;
				}
				const orchestrator = make_orchestrator();
				(props.control.barrier as unknown as Barrier) = { orchestrator };
				orchestrator.next(true); // kickoff
			}

			const orchestrator = (props.control.barrier as unknown as Barrier).orchestrator;

			if (orchestrating_lock) await orchestrating_lock;

			if (node.dataset.dirty) {
				let handler: null | Awaited<ReturnType<SubmitFunction>> = null;
				if (props?.custom_submit) {
					try {
						let cancelled = false;
						handler = await props.custom_submit({
							...input,
							cancel: () => {
								cancelled = true;
							}
						});
						if (cancelled) {
							delete node.dataset.dirty;
							cancel();
							orchestrator.next(true);
						}
					} catch {
						cancel();
						orchestrator.next(false);
						return;
					}
				}
				return async (output) => {
					let updated = false;
					const update: typeof output.update = async (options) => {
						updated = true;
						if (output.result.type === 'success' || output.result.type === 'redirect') {
							delete node.dataset.dirty;
							orchestrator.next(true);
							// Only do update if we are orchestrating
							void (orchestrating_lock && (await output.update(options)));
						} else {
							orchestrator.next(false);
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
