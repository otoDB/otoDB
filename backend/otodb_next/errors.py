"""Error responses matching django-ninja's wire shapes, so migrated endpoints
are drop-in replacements for the frontend:

- ApiError            -> ``{"code": <ErrorCode int>, "data": {...}?}`` (mirror
  of otodb.api.common.ApiError + its exception handler)
- 404 Not Found       -> ``{"detail": "Not Found"}``
- 401 Unauthorized    -> ``{"detail": "Unauthorized"}``
- 403 Forbidden       -> ``{"detail": "Forbidden"}`` (ninja HttpError(403))
- 429 Throttled       -> ``{"code": 429}`` (ErrorCode.RATE_LIMITED)

Known divergence: request validation errors are Litestar-shaped 400s, not
ninja's pydantic-shaped 422s. The frontend's generated client never branches
on validation bodies, so parity there is not maintained.
"""

from litestar import Request, Response
from litestar.exceptions import (
	NotAuthorizedException,
	NotFoundException,
	PermissionDeniedException,
	TooManyRequestsException,
)


class ApiError(Exception):
	"""Mirror of otodb.api.common.ApiError."""

	def __init__(self, status: int, code: int, data: dict | None = None) -> None:
		super().__init__(str(code))
		self.status = status
		self.code = code
		self.data = data


def _handle_api_error(request: Request, exc: ApiError) -> Response:
	body: dict = {'code': int(exc.code)}
	if exc.data is not None:
		body['data'] = exc.data
	return Response(body, status_code=exc.status)


def _detail(status_code: int, detail: str):
	def handler(request: Request, exc: Exception) -> Response:
		return Response({'detail': detail}, status_code=status_code)

	return handler


def _handle_throttled(request: Request, exc: Exception) -> Response:
	return Response({'code': 429}, status_code=429)  # ErrorCode.RATE_LIMITED


exception_handlers = {
	ApiError: _handle_api_error,
	NotFoundException: _detail(404, 'Not Found'),
	NotAuthorizedException: _detail(401, 'Unauthorized'),
	PermissionDeniedException: _detail(403, 'Forbidden'),
	TooManyRequestsException: _handle_throttled,
}
