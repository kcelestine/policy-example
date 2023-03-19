import enum
from datetime import datetime

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from domain.quiz_topic import QuizTopic


class QuizStatusCode(enum.Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    EXPIRED = "EXPIRED"


class QuizUserRole(enum.Enum):
    PLAYER = "PLAYER"
    COMMANDER = "COMMANDER"


@dataclass_json
@dataclass
class QuizState(QuizTopic):
    quiz_code: int
    status: QuizStatusCode
    expires: datetime
    user_role: QuizUserRole
    user_token: str
