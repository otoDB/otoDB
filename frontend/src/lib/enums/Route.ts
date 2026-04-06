/**
 * Recent Update
 */

export const Route = {
	UNKNOWN: { id: 0, title: 'Unknown' },

	TAGWORK_ALIAS: { id: 1, title: 'Tag: Alias' },
	TAGWORK_UNALIAS: { id: 2, title: 'Tag: Unalias' },
	TAGWORK_DELETE: { id: 3, title: 'Tag: Delete' },
	TAGWORK_UPDATE: { id: 4, title: 'Tag: Update' },
	TAGWORK_SET_BASE: { id: 5, title: 'Tag: Set Base' },
	TAGWORK_ADD_LANG_PREF: { id: 6, title: 'Tag: Add Language' },
	TAGWORK_EDIT_WIKI: { id: 7, title: 'Tag: Edit Wiki' },
	TAGWORK_EDIT_CONNECTIONS: { id: 8, title: 'Tag: Edit Connections' },

	SONGTAG_UPDATE: { id: 20, title: 'Song Attribute: Update' },
	SONGTAG_SET_TAGS: { id: 21, title: 'Song: Set Tags' },

	SONGRELATION_CREATE: { id: 30, title: 'Song: Create Relation' },
	SONGRELATION_DELETE: { id: 31, title: 'Song: Delete Relation' },

	MEDIAWORK_DELETE: { id: 40, title: 'Work: Delete' },
	MEDIAWORK_SET_TAGS: { id: 41, title: 'Work: Set Tags' },
	MEDIAWORK_REMOVE_TAG: { id: 42, title: 'Work: Remove Tag' },
	MEDIAWORK_UPDATE_CREATOR_ROLES: { id: 43, title: 'Work: Update Creator Roles' },
	MEDIAWORK_TOGGLE_SAMPLE: { id: 44, title: 'Work: Toggle Sample' },
	MEDIAWORK_UPDATE: { id: 45, title: 'Work: Update' },
	MEDIAWORK_MERGE: { id: 46, title: 'Work: Merge' },
	MEDIAWORK_CREATE: { id: 47, title: 'Work: Create' },

	WORKRELATION_CREATE: { id: 50, title: 'Work: Create Relation' },
	WORKRELATION_DELETE: { id: 51, title: 'Work: Delete Relation' },

	WORKSOURCE_CREATE: { id: 60, title: 'Upload: Create' },
	WORKSOURCE_UNBIND: { id: 61, title: 'Upload: Unbind' },
	WORKSOURCE_SET_ORIGIN: { id: 62, title: 'Upload: Set Origin' },
	WORKSOURCE_REFRESH: { id: 63, title: 'Upload: Refresh' },
	WORKSOURCE_ASSIGN: { id: 64, title: 'Upload: Assign' },
	WORKSOURCE_REJECT: { id: 65, title: 'Upload: Reject' },
	WORKSOURCE_UPDATE: { id: 66, title: 'Upload: Update' },

	ROLLBACK: { id: 100, title: 'Rollback' }
} as const satisfies Record<string, { id: number; title: string }>;

/**
 * @deprecated
 */
export function resolveRouteKeyById(id: number): keyof typeof Route {
	return Object.entries(Route).find(([_, value]) => value.id === id)?.[0] as keyof typeof Route;
}
