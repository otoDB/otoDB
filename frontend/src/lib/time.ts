import { m } from '$lib/paraglide/messages';

const MINUTE = 60;
const HOUR = MINUTE * 60;
const DAY = HOUR * 24;
const WEEK = DAY * 7;
const MONTH = DAY * 30;
const YEAR = DAY * 365;

export function formatRelative(date: Date, locale: string): string {
	const diff = (date.getTime() - Date.now()) / 1000;
	const elapsed = Math.abs(diff);

	if (elapsed <= 1) return m.busy_hour_bee_gasp();

	const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'always' });

	// prettier-ignore
	const [divisor, unit]: [number, Intl.RelativeTimeFormatUnit] =
		elapsed > YEAR   * 2 ? [YEAR,   'year']   :
		elapsed > MONTH  * 2 ? [MONTH,  'month']  :
		elapsed > WEEK   * 2 ? [WEEK,   'week']   :
		elapsed > DAY    * 1 ? [DAY,    'day']    :
		elapsed > HOUR   * 1 ? [HOUR,   'hour']   :
		elapsed > MINUTE * 2 ? [MINUTE, 'minute'] :
		                       [1,      'second'];

	return rtf.format(Math.trunc(diff / divisor), unit);
}

export function formatAbsolute(date: Date, locale: string): string {
	return new Intl.DateTimeFormat(locale, { dateStyle: 'short', timeStyle: 'short' }).format(date);
}
