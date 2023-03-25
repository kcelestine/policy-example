from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class QuizStartRequest:
    topic_id: str
    user_name: str
    question_seconds: int = 20


@dataclass_json
@dataclass
class QuizJoinRequest:
    quiz_code: int
    user_name: str


@dataclass_json
@dataclass
class QuizStatusRequest:
    quiz_code: int
    user_token: str


@dataclass_json
@dataclass
class ScheduleQuizRequest:
    quiz_code: int
    user_token: str
    delay_seconds: int
