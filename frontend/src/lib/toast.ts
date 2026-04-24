import { toast } from 'svelte-sonner';
import { m } from '$lib/paraglide/messages';
import { ErrorCode } from '$lib/schema';

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

const errorCodeMessages: Partial<
	Record<ErrorCode, (payload: Record<string, unknown>) => string | null>
> = {
	[ErrorCode.Source_Flagged]: () => m.antsy_main_puffin_dust(),
	[ErrorCode.Source_Unapproved]: () => m.clean_civil_jellyfish_promise(),
	[ErrorCode.Self_Moderation]: () => m.fluffy_noble_gadfly_adapt(),
	[ErrorCode.Name_Slug_Mismatch]: (payload) =>
		typeof payload.name === 'string' &&
		typeof payload.slug === 'string' &&
		typeof payload.result === 'string'
			? m.caring_each_leopard_hint({
					name: payload.name,
					slug: payload.slug,
					result: payload.result
				})
			: null
};

export const callErrorCodeToast = (code: number, payload: Record<string, unknown>) => {
	const message = errorCodeMessages[code as ErrorCode]?.(payload);
	toast.error(message ?? m.green_due_javelina_pop());
};
