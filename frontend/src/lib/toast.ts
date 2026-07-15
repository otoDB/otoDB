import { formatApiErrorMessage, type ApiError } from '$lib/errors';
import { m } from '$lib/paraglide/messages';
import { toast } from 'svelte-sonner';

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

export const callSavingToast = (p: Promise<{ error?: unknown }>) =>
	toast.promise(
		p.then((r) => {
			if (r?.error) throw r.error;
			return r;
		}),
		{
			loading: m.zippy_broad_porpoise_seek(),
			success: m.deft_full_quail_coax(),
			error: m.green_due_javelina_pop()
		}
	);

export const callApiErrorToast = (err: ApiError) => toast.error(formatApiErrorMessage(err));
