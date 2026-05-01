import { m } from '$lib/paraglide/messages';
import { ErrorCode } from '$lib/schema';
import { fail } from '@sveltejs/kit';

export type ErrorPayload = Record<string, unknown>;
export type ApiError = {
	code: ErrorCode | -1;
	data?: ErrorPayload | null;
};

export const formatApiErrorMessage = (err: ApiError): string => {
	switch (err.code) {
		case ErrorCode.Source_Flagged:
			return m.antsy_main_puffin_dust();
		case ErrorCode.Source_Unapproved:
			return m.clean_civil_jellyfish_promise();
		case ErrorCode.Self_Moderation:
			return m.fluffy_noble_gadfly_adapt();
		case ErrorCode.Login_Failed:
			return m.brave_stark_orca_note();
		case ErrorCode.Not_Logged_In:
			return m.major_keen_oryx_fall();
		case ErrorCode.Username_Taken:
			return m.red_raw_duck_evoke();
		case ErrorCode.Source_Has_Work:
			return m.grim_loose_crane_lift();
		case ErrorCode.Bad_Url:
			return m.noble_bright_marlin_trip();
		case ErrorCode.Editor_Only:
			return m.clear_stout_otter_guide();
		case ErrorCode.No_Matching_Entities:
			return m.vast_calm_raven_seek();
		case ErrorCode.No_More_Upload_Slots:
			return m.sharp_keen_puffin_wait();
		case ErrorCode.No_More_Appeal_Slots:
			return m.tiny_snug_otter_linger();
		case ErrorCode.Validation_Error:
			return m.plain_brief_owl_pause();
		case ErrorCode.Flag_Not_Approved:
			return m.mealy_grim_elk_stop();
		case ErrorCode.Flag_Pending_Flag:
			return m.bold_sunny_stork_halt();
		case ErrorCode.Flag_Pending_Appeal:
			return m.quiet_still_mole_guard();
		case ErrorCode.Flag_Limit_Reached:
			return m.stern_few_quail_rest();
		case ErrorCode.Appeal_Pending:
			return m.calm_brisk_swan_queue();
		case ErrorCode.Tag_Has_Information:
			return m.that_new_mayfly_spur();
		case ErrorCode.Name_Slug_Mismatch:
			if (
				typeof err.data?.name === 'string' &&
				typeof err.data?.slug === 'string' &&
				typeof err.data?.result === 'string'
			)
				return m.caring_each_leopard_hint({
					name: err.data.name,
					slug: err.data.slug,
					result: err.data.result
				});
			else return m.green_due_javelina_pop();
		default:
			return m.green_due_javelina_pop();
	}
};

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
