import pytest


@pytest.fixture(autouse=True)
def enable_request_cache():
	"""Override the DB-backed autouse fixture from the parent conftest -- these
	tests exercise pure ASGI middleware and must not require a database."""
	yield
