export const versions = {
	PRE_ALPHA: { name: 'Pre-Alpha', timestamp: 1752505560412 },
	ALPHA: { name: 'Alpha', timestamp: 1766984874569 },
	BETA: { name: 'Beta', timestamp: Number.POSITIVE_INFINITY }
} as const satisfies Record<string, { name: string; timestamp: number }>;

export const currentVersion: keyof typeof versions = 'BETA';

export const getVersionKey = (date: Date): keyof typeof versions => {
	const timestamp = date.getTime();
	return (Object.keys(versions) as (keyof typeof versions)[]).find(
		(key) => timestamp <= versions[key].timestamp
	)!;
};
