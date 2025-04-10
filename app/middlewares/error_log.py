# from datetime import datetime
#
# from fastapi import Request, FastAPI
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.responses import Response
#
# from app.models.error_log import ErrorLog
# from app.backend.db_depends import get_db
#
#
# class ErrorLoggingMiddleware(BaseHTTPMiddleware):
#     def __init__(self, app: FastAPI) -> None:
#         super().__init__(app)
#
#     async def dispatch(self, request: Request, call_next) -> Response:
#         response = await call_next(request)
#
#         error_log = ErrorLog(
#             path=str(request.url.path),
#             method=request.method,
#             status_code=response.status_code,
#             error_message=response.body,
#             timestamp=datetime.now()
#         )
#         db = get_db()
#         db.add(error_log)
#         db.commit()