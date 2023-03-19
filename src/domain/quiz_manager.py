import datetime
import os
import random
import re
import uuid
from typing import List, Optional

import redis

from domain.quiz_data import QuizData
from domain.quiz_requests import QuizStartRequest
from domain.quiz_state import QuizState, QuizStatusCode, QuizUserRole
from domain.quiz_topic import QuizTopic
from settings import settings


class QuizManager:
    PENDING_QUIZ_EXPIRATION_SECONDS = 10 * 60

    def __init__(self):
        self.quizes: List[QuizData] = []
        self._read_quizes()
        self.redis_cli = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    def get_quiz_topics(self) -> List[QuizTopic]:
        return [
            QuizTopic(id=q.id, name=q.name) for q in self.quizes
        ]

    def start_quiz(self, request_data: QuizStartRequest) -> Optional[QuizState]:
        expires = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=self.PENDING_QUIZ_EXPIRATION_SECONDS)
        quizes = [q for q in self.quizes if q.id == request_data.topic_id]
        if not quizes:
            raise Exception(f"Quiz #{request_data.topic_id} wasn't found out of "
                            f"{self.quizes} quizes")
        quiz = quizes[0]
        q_state = QuizState(
            id=quiz.id,
            name=quiz.name,
            quiz_code=random.randint(0, 100000),
            status=QuizStatusCode.PENDING,
            expires=expires,
            user_role=QuizUserRole.COMMANDER,
            user_token=str(uuid.uuid4())
        )
        self.redis_cli.set(
            f"quiz_{q_state.quiz_code}",
            quiz.to_json(),
            ex=self.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        return q_state

    def _read_quizes(self) -> None:
        quiz_path = settings.quiz_path
        # list directories q01 ...
        for dir_name, dir_path in [
            (o, os.path.join(quiz_path, o)) for o in os.listdir(quiz_path)
                if os.path.isdir(os.path.join(quiz_path, o))]:
            if not re.match(r'^q\d+$', dir_name):
                continue
            # read "quiz_data.json"
            self._read_quiz(dir_path)

    def _read_quiz(self, quiz_path: str) -> None:
        file_path = os.path.join(quiz_path, "quiz_data.json")
        with open(file_path, "r") as file:
            json_data = file.read()
        self.quizes.append(QuizData.from_json(json_data))


quiz_manager = QuizManager()
