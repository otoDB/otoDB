import { describe, expect, it } from 'vitest';
import { bucketByMonth, niceTicks } from './history';

describe('bucketByMonth', () => {
	it('returns nothing for an empty series', () => {
		expect(bucketByMonth([])).toEqual([]);
	});

	it('keeps the last running total of each month', () => {
		const actual = bucketByMonth([
			{ date: '2024-01-03', total: 2 },
			{ date: '2024-01-20', total: 5 },
			{ date: '2024-02-01', total: 6 }
		]);

		expect(actual).toEqual([
			{ month: '2024-01', total: 5 },
			{ month: '2024-02', total: 6 }
		]);
	});

	it('fills months with no additions, carrying the running total', () => {
		const actual = bucketByMonth([
			{ date: '2024-01-03', total: 4 },
			{ date: '2024-04-10', total: 5 }
		]);

		expect(actual).toEqual([
			{ month: '2024-01', total: 4 },
			{ month: '2024-02', total: 4 },
			{ month: '2024-03', total: 4 },
			{ month: '2024-04', total: 5 }
		]);
	});

	it('rolls over into the next year', () => {
		const actual = bucketByMonth([
			{ date: '2023-12-31', total: 1 },
			{ date: '2024-01-01', total: 2 }
		]);

		expect(actual.map((b) => b.month)).toEqual(['2023-12', '2024-01']);
	});
});

describe('niceTicks', () => {
	it('starts at zero and ends at or above the maximum', () => {
		const ticks = niceTicks(1234);

		expect(ticks[0]).toBe(0);
		expect(ticks[ticks.length - 1]).toBeGreaterThanOrEqual(1234);
	});

	it('uses a round step', () => {
		expect(niceTicks(1000)).toEqual([0, 250, 500, 750, 1000]);
		expect(niceTicks(8)).toEqual([0, 2, 4, 6, 8]);
	});

	it('never collapses to a single zero tick', () => {
		expect(niceTicks(0)).toEqual([0, 1]);
	});
});
