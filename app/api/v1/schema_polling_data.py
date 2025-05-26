from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FileData(BaseModel, extra="forbid"):

    POLLING_DATA_FILE_ID: int
    POLLING_DATA_FILE_NAME: str
    VALID_FROM: datetime
    VALID_TO: Optional[datetime]
    DATA_INSERTED: datetime
    DATA_UPDATED: Optional[datetime]


class PollingAttributes(BaseModel, extra="forbid"):
    POLLING_DATA_ATTRIBUTE_ID: int
    POLLING_DATA_ATTRIBUTE: str
    VALID_FROM: datetime
    VALID_TO: Optional[datetime] = None
    DATA_INSERTED: datetime
    DATA_UPDATED: Optional[datetime] = None
    POLLING_DATA_FILE_ID: int


class FileDataResponse(BaseModel, extra="forbid"):
    data: str
    message: str
    status: int
    success: bool
