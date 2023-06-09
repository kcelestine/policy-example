import enum
from datetime import datetime
from typing import List, Optional, Tuple

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from domain.quiz_data import QuizQuestion, QuizData
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
    starts_at: Optional[datetime] = None
    question_seconds: int = 10
    cur_question: Optional[QuizQuestion] = None
    cur_question_index: Tuple[int, int] = -1, 0
    updates_in_seconds: int = -1


@dataclass_json
@dataclass
class QuizPlayerAnswer:
    answer: List[int]
    answer_given_seconds: int = -1


@dataclass_json
@dataclass
class QuizPlayer:
    user_token: str
    name: str
    user_role: QuizUserRole
    answers: List[QuizPlayerAnswer]


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


@dataclass_json
@dataclass
class QuizResultsPlayer:
    name: str
    correct_answers: int
    total_answering_time: float
    answers: List[QuizPlayerAnswer]


@dataclass_json
@dataclass
class QuizResults:
    quiz_id: str
    quiz_name: str
    started_at: datetime
    players: List[QuizResultsPlayer]


@dataclass_json
@dataclass
class QuizResultsAndData:
    quiz_results: QuizResults
    quiz_data: QuizData
