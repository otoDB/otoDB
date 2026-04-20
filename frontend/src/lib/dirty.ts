import { enhance } from '$app/forms';
import { m } from '$lib/paraglide/messages';

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
		| undefined = undefined
) => {
	node.dataset.priority = props?.priority?.toString();
	node.addEventListener('change', () => {
		node.dataset.dirty = 'true';
	});

	return enhance(node, async ({ cancel }) => {
		const dirty_forms = Array.from(document.querySelectorAll('form')).filter(isFormDirty);
		const me_dirty = node.dataset.dirty;

		if (props?.manual_post) cancel();

		if (props?.barrier) {
			const first = !props?.barrier.reached?.length;
			if (first) {
				if (!dirty_forms.every((f) => f.reportValidity())) {
					cancel();
					return;
				}

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
			if (me_dirty) {
				const my_id = props.barrier.forms!.indexOf(node);
				if (first)
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
		} else if (dirty_forms.some((f) => f !== node) && !confirm(m.active_lime_panther_buzz())) {
			cancel();
			props?.manual_post?.p.reject();
		}
		props?.manual_post?.p.resolve();
	});
};
