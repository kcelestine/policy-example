import enum
from datetime import datetime
from typing import List

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


@dataclass_json
@dataclass
class QuizPlayer:
    user_token: str
    name: str
    user_role: QuizUserRole


@dataclass_json
@dataclass
class UserQuizState:
    state: QuizState
    user: QuizPlayer
    all_user_names: List[str]


@dataclass_json
@dataclass
class QuizPlayers:
    players: List[QuizPlayer]
