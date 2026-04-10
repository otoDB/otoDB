export const Version = {
	PRE_ALPHA: { name: 'Pre-Alpha', timestamp: 1752505560412 },
	ALPHA: { name: 'Alpha', timestamp: 1766984874569 },
	BETA: { name: 'Beta', timestamp: Number.POSITIVE_INFINITY }
} as const satisfies Record<string, { name: string; timestamp: number }>;

export const currentVersion: keyof typeof Version = 'BETA';

export const getVersionKey = (date: Date): keyof typeof Version => {
	const timestamp = date.getTime();
	return (Object.keys(Version) as (keyof typeof Version)[]).find(
		(key) => timestamp <= Version[key].timestamp
	)!;
};
