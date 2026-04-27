import pytest

from otodb.models import MediaWork, TagWork, TagWorkInstance
from otodb.models.enums import WorkTagCategory


def make_tag(name, category):
	return TagWork.objects.create(name=name, category=category)


@pytest.fixture
def creator_tag():
	return make_tag('creator_tag', WorkTagCategory.CREATOR)


@pytest.fixture
def song_tag():
	return make_tag('song_tag', WorkTagCategory.SONG)


@pytest.fixture
def source_tag():
	return make_tag('source_tag', WorkTagCategory.SOURCE)


@pytest.fixture
def general_tag():
	return make_tag('general_tag', WorkTagCategory.GENERAL)


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestGetTagsNeeded:
	def test_returns_works_missing_tags(self, work_client, creator_tag):
		work = MediaWork.objects.create(title='No Tags Work')
		res = work_client.get('/tags_needed')
		assert res.status_code == 200
		ids = [int(w['id']) for w in res.json()['items']]
		assert work.id in ids

	def test_ordered_by_most_missing_tags_first(
		self, work_client, creator_tag, song_tag, source_tag, general_tag
	):
		# work_a: missing all 4
		work_a = MediaWork.objects.create(title='Missing All')

		# work_b: missing 1 (only creator)
		work_b = MediaWork.objects.create(title='Missing One')
		work_b.tags.add(song_tag)
		work_b.tags.add(source_tag)
		work_b.tags.add(general_tag)

		res = work_client.get('/tags_needed')
		assert res.status_code == 200
		ids = [int(w['id']) for w in res.json()['items']]
		assert ids.index(work_a.id) < ids.index(work_b.id)

	def test_used_as_source_creator_satisfies_source_requirement(
		self, work_client, creator_tag, song_tag, general_tag, source_tag
	):
		# work_a: SOURCE not satisfied — appears in list
		work_a = MediaWork.objects.create(title='Missing Source')
		work_a.tags.add(creator_tag)
		work_a.tags.add(song_tag)
		work_a.tags.add(general_tag)

		# work_b: SOURCE satisfied via creator used_as_source — all requirements met, not in list
		work_b = MediaWork.objects.create(title='Source via Creator')
		work_b.tags.add(creator_tag)
		work_b.tags.add(song_tag)
		work_b.tags.add(general_tag)
		twi = TagWorkInstance.objects.get(work=work_b, work_tag=creator_tag)
		twi.used_as_source = True
		twi.save()

		res = work_client.get('/tags_needed')
		assert res.status_code == 200
		ids = [int(w['id']) for w in res.json()['items']]
		assert work_a.id in ids
		assert work_b.id not in ids

	def test_deprecated_tag_does_not_fulfill_requirement(
		self, work_client, creator_tag, song_tag, source_tag, general_tag
	):
		deprecated_creator = make_tag('old_creator', WorkTagCategory.CREATOR)
		deprecated_creator.deprecated = True
		deprecated_creator.save()

		# work_a: only a deprecated CREATOR tag — CREATOR requirement not met, appears in list
		work_a = MediaWork.objects.create(title='Deprecated Creator Only')
		work_a.tags.add(deprecated_creator)
		work_a.tags.add(song_tag)
		work_a.tags.add(source_tag)
		work_a.tags.add(general_tag)

		# work_b: active CREATOR tag — all requirements met, does not appear in list
		work_b = MediaWork.objects.create(title='Active Creator')
		work_b.tags.add(creator_tag)
		work_b.tags.add(song_tag)
		work_b.tags.add(source_tag)
		work_b.tags.add(general_tag)

		res = work_client.get('/tags_needed')
		assert res.status_code == 200
		ids = [int(w['id']) for w in res.json()['items']]
		assert work_a.id in ids
		assert work_b.id not in ids
