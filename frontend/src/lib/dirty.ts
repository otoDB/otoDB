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

type Orchestrator = AsyncGenerator<void, void, null | (() => Promise<void> | void)>;
type Barrier = {
	orchestrator: Orchestrator;
	forms: HTMLFormElement[];
};

export type Control = {
	barrier: { [K in keyof Barrier]?: never };
	priority: number;
};

export const dirtyEnhance = (
	node: HTMLFormElement,
	props?: { custom_submit?: SubmitFunction } & (Control | { [K in keyof Control]?: never })
) => {
	if (props?.priority) node.dataset.priority = props.priority.toString();
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
	});

	if (props?.barrier) {
		const barrier = props.barrier as unknown as Barrier;
		if (!barrier.forms) (barrier as Partial<Barrier>).forms = [];
		barrier.forms.push(node);
	}

	return enhance(node, async (input) => {
		const { cancel } = input;
		const dirty_forms = Array.from(document.querySelectorAll('form')).filter(isFormDirty);

		if (props?.barrier) {
			const first = !Object.hasOwn(props.barrier, 'orchestrator');
			let orchestrating_lock: Promise<void> | null = null;
			if (first) {
				// Check HTML form validation before proceeding
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}
				dirty_forms.sort((a, b) => +(a.dataset.priority ?? 0) - +(b.dataset.priority ?? 0));
				// Lock all related forms (not just dirty ones)
				(props.barrier as unknown as Barrier).forms.forEach((f) => {
					f.inert = true;
				});

				let resolve_orchestrator: null | ReturnType<typeof Promise.withResolvers<void>>['resolve'] =
					null;
				if (node.dataset.dirty)
					({ promise: orchestrating_lock, resolve: resolve_orchestrator } =
						Promise.withResolvers<void>());
				const my_id = dirty_forms.indexOf(node);
				async function* make_orchestrator(): Orchestrator {
					if (dirty_forms.length === 0) {
						const handler = yield;
						if (handler) await handler();
					} else {
						const handlers = [];
						for (let i = 0; i < dirty_forms.length; i++) {
							if (i !== my_id) dirty_forms![i].requestSubmit();
							else void (resolve_orchestrator && resolve_orchestrator());
							const handler = yield;
							if (handler) handlers.push(handler);
						}
						for (const handler of handlers) await handler();
					}
				}
				const orchestrator = make_orchestrator();
				(props.barrier as unknown as Barrier).orchestrator = orchestrator;
				orchestrator.next(); // kickoff
			}

			const barrier = props.barrier as unknown as Barrier;
			const fail = () => {
				barrier.forms.forEach((f) => {
					f.inert = false;
				});
				(barrier as Partial<Barrier>).orchestrator = undefined;
			};
			const orchestrator = barrier.orchestrator;

			if (orchestrating_lock) await orchestrating_lock;

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
						orchestrator.next();
					}
				} catch {
					cancel();
					fail();
					return;
				}
			}
			return async (output) => {
				let updated = false;
				const update: typeof output.update = async (options) => {
					updated = true;
					if (output.result.type === 'success' || output.result.type === 'redirect') {
						delete node.dataset.dirty;
						// Only do update if we are first
						orchestrator.next(first ? () => output.update(options) : null);
					} else {
						fail();
						await output.update(options);
					}
				};
				if (handler) await handler({ ...output, update });
				if (!updated) await update();
			};
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
