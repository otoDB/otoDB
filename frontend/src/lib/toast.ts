import { toast } from 'svelte-sonner';
import { m } from './paraglide/messages';
import { ErrorCode } from './enums';

export const callErrorToast = (message: string) => toast.error(message, {});

export const callSuccessToast = (message: string) => toast.success(message, {});

export const callInfoToast = (message: string) => toast.info(message, {});

export const callDismissToast = (message: string) =>
	toast(message, {
		action: {
			label: 'X',
			onClick: () => {}
		},
		duration: Number.POSITIVE_INFINITY
	});

export const callSavingToast = (p: Promise<any>) =>
	toast.promise(p, {
		loading: m.zippy_broad_porpoise_seek(),
		success: m.deft_full_quail_coax(),
		error: m.green_due_javelina_pop()
	});

export const callErrorCodeToast = (code: number, payload: Record<string, unknown>) => {
	switch (code) {
		case ErrorCode.NAME_SLUG_MISMATCH:
			if (
				'name' in payload &&
				typeof payload.name === 'string' &&
				'slug' in payload &&
				typeof payload.slug === 'string' &&
				'result' in payload &&
				typeof payload.result === 'string'
			)
				toast.error(
					m.caring_each_leopard_hint({
						name: payload.name,
						slug: payload.slug,
						result: payload.result
					})
				);
			else {
				// TODO: more detailed message for the broken payload.
				toast.error(m.green_due_javelina_pop());
			}
			break;
		default:
			toast.error(m.green_due_javelina_pop());
			break;
	}
};
