from typing import Any, Dict

from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: Any = "",
        headers: Dict[str, str] = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=message)
        self.headers = headers
