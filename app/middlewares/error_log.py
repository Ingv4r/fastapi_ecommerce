import logging

from fastapi import Request, HTTPException
from starlette.types import Scope, Receive, Send, Message, ASGIApp

from app.backend.db import SessionLocal
from app.models.error_log import ErrorLog


async def _get_error_content(response) -> str:
    return (await response.body()).decode()


class ErrorLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive)
        status_code = 500
        response_body = b""
        error_message = ""

        async def custom_send(message: Message):
            nonlocal status_code, response_body

            if message["type"] == "http.response.start":
                status_code = message["status"]

            elif message["type"] == "http.response.body":
                response_body += message.get("body", b"")

            await send(message)

        try:
            await self.app(scope, receive, custom_send)
        except HTTPException as exc:
            status_code = exc.status_code
            error_message = exc.detail
            await self._send_error_response(send, status_code, error_message)
        except Exception as exc:
            logging.exception("Unhandled exception")
            status_code = 500
            error_message = str(exc)
            await self._send_error_response(send, status_code, "Internal Server Error")

        if status_code >= 400:
            self.log_error(
                request=request,
                status_code=status_code,
                error_message=error_message or response_body.decode(),
            )

    async def _send_error_response(self, send, status_code: int, message: str):
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [(b"content-type", b"text/plain; charset=utf-8")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": message.encode(),
            }
        )

    def log_error(self, request: Request, status_code: int, error_message: str):
        with SessionLocal() as session:
            try:
                error_log = ErrorLog(
                    path=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    error_message=error_message[:255],  # Ограничение длины
                )
                session.add(error_log)
                session.commit()
            except Exception as e:
                logging.error(f"Error saving log: {str(e)}")
                session.rollback()
