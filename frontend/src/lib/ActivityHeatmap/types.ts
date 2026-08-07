import type { components } from '$lib/schema';

/** A single UTC day of the contribution heatmap. */
export type ActivityDay = components['schemas']['ActivityDaySchema'];

/** A user's contribution activity over a rolling 365-day window. */
export type ProfileActivity = components['schemas']['ProfileActivitySchema'];
