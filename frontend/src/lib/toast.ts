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
	[ErrorCode.Login_Failed]: () => m.brave_stark_orca_note(),
	[ErrorCode.Username_Taken]: () => m.red_raw_duck_evoke(),
	[ErrorCode.Source_Has_Work]: () => m.grim_loose_crane_lift(),
	[ErrorCode.Bad_Url]: () => m.noble_bright_marlin_trip(),
	[ErrorCode.Editor_Only]: () => m.clear_stout_otter_guide(),
	[ErrorCode.No_Matching_Entities]: () => m.vast_calm_raven_seek(),
	[ErrorCode.No_More_Upload_Slots]: () => m.sharp_keen_puffin_wait(),
	[ErrorCode.No_More_Appeal_Slots]: () => m.tiny_snug_otter_linger(),
	[ErrorCode.Validation_Error]: () => m.plain_brief_owl_pause(),
	[ErrorCode.Flag_Not_Approved]: () => m.mealy_grim_elk_stop(),
	[ErrorCode.Flag_Pending_Flag]: () => m.bold_sunny_stork_halt(),
	[ErrorCode.Flag_Pending_Appeal]: () => m.quiet_still_mole_guard(),
	[ErrorCode.Flag_Limit_Reached]: () => m.stern_few_quail_rest(),
	[ErrorCode.Appeal_Pending]: () => m.calm_brisk_swan_queue(),
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
