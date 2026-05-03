import { m } from '$lib/paraglide/messages';
import { ErrorCode } from '$lib/schema';
import { fail } from '@sveltejs/kit';

export type ErrorPayload = Record<string, unknown>;
export type ApiError = {
	code: ErrorCode | -1;
	data?: ErrorPayload | null;
};

const errorCodeMessages: Partial<Record<ErrorCode, (payload: ErrorPayload) => string | null>> = {
	[ErrorCode.Source_Flagged]: () => m.antsy_main_puffin_dust(),
	[ErrorCode.Source_Unapproved]: () => m.clean_civil_jellyfish_promise(),
	[ErrorCode.Self_Moderation]: () => m.fluffy_noble_gadfly_adapt(),
	[ErrorCode.Login_Failed]: () => m.brave_stark_orca_note(),
	[ErrorCode.Not_Logged_In]: () => m.major_keen_oryx_fall(),
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
	[ErrorCode.Tag_Has_Information]: () => m.that_new_mayfly_spur(),
	[ErrorCode.Thumbnail_Source_Required]: () => m.sleek_brave_heron_choose(),
	[ErrorCode.Tag_With_Instances_Merge_Requires_Editor]: () => m.witty_brisk_hawk_merge(),
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

export const formatApiErrorMessage = (err: ApiError): string =>
	errorCodeMessages[err.code as ErrorCode]?.(err.data ?? {}) ?? m.green_due_javelina_pop();

export const parseApiErrorResponse = async (response: Response): Promise<ApiError> => {
	try {
		const body = await response.clone().json();
		if (body && typeof body.code === 'number')
			return { code: body.code, data: body.data ?? {} };
	} catch {
		// fall through to default error
	}
	return { code: -1, data: {} };
};

export const apiFail = <T extends Record<string, unknown>>(err: ApiError, extra: T = {} as T) =>
	fail(400, { failed: true as const, code: err.code, errorData: err.data ?? {}, ...extra });
