import client from './api';
import { languages } from './enums/language';
import { setLocale } from './paraglide/runtime';

export const set_lang = async (lang: keyof typeof languages, logged_in: boolean) => {
	if (logged_in) {
		await client.POST('/api/profile/prefs', {
			fetch,
			body: {
				LANGUAGE: languages[lang].id
			}
		});
	}
	setLocale(lang);
};
