from collections import Counter
from pathlib import Path

OTODB_NEXT = Path(__file__).resolve().parents[2] / 'otodb_next'

EXPECTED = {
	'enums.py': 1,  # do_not_call_in_templates, removable at cutover
	'models/account.py': 1,  # READ-ONLY until auth migrates (last)
	'models/base.py': 2,  # the convention itself
	'models/content_type.py': 1,  # READ-ONLY; post-Django seeding decision
	'models/media.py': 1,  # MediaWork READ-ONLY (status/merge/cascades)
	'models/notification.py': 3,  # comment/threadpost FKs not ported
	'models/tag.py': 1,  # TagWork READ-ONLY (tagulous + cascade set)
	'models/work_source.py': 1,  # create/refresh/delete stay Django-side
}


def test_todo_port_inventory():
	found = Counter()
	for path in OTODB_NEXT.rglob('*.py'):
		rel = path.relative_to(OTODB_NEXT).as_posix()
		for line in path.read_text(encoding='utf-8').splitlines():
			if 'TODO(port)' in line:
				found[rel] += 1

	assert dict(found) == EXPECTED, (
		'TODO(port) markers changed. If you resolved one, update EXPECTED here '
		'AND make sure the ported behavior has tests; if you added one, record '
		'it here so it stays visible.'
	)
