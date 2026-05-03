from django.http import HttpRequest

from otodb.models.revision import set_skip_dirty_tracking

READ_ONLY_HTTP_METHODS = frozenset({'GET', 'HEAD', 'OPTIONS'})


class SkipDirtyFieldsOnReadMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request: HttpRequest):
		if request.method in READ_ONLY_HTTP_METHODS:
			set_skip_dirty_tracking(True)
			try:
				return self.get_response(request)
			finally:
				set_skip_dirty_tracking(False)
		return self.get_response(request)
