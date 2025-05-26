from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra


class BodyTypeEnum(str, Enum):

    MALE = "male"
    FEMALE = "female"
    DIVERSE = "diverse"


class ExecutionModeEnum(str, Enum):
    SYNC = "sync"
    ASYNC = "async"


class ValidationItems(BaseModel, extra=Extra.forbid):
    item_name: Optional[str]
    item_message: Optional[str]


class HttpError(BaseModel, extra=Extra.forbid):
    message: str
    items: Optional[List[ValidationItems]]


class AnswerEnum(str, Enum):
    YES = "Y"
    No = "N"


class ProcessingStatusEnum(str, Enum):

    NEW = "new"
    UPDATE = "updating"
    SUCCESS = "success"
    FAIL = "fail"
    WAITING = "waiting"


class LanguageEnum(str, Enum):
    DE = "de"
    EN = "en"
    AR = "ar"


class JobExecutionResult(str, Enum):
    START = "S"
    FINISHED = "F"
    ERROR = "E"
    INFO = "I"
    WARN = "W"
