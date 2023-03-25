import datetime
import os
import random
import re
import uuid
from typing import List, Tuple

import redis

from domain.quiz_data import QuizData
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest
from domain.quiz_state import QuizState, QuizStatusCode, QuizUserRole, QuizPlayers, QuizPlayer, UserQuizState
from domain.quiz_topic import QuizTopic
from settings import settings


class QuizManager:
    PENDING_QUIZ_EXPIRATION_SECONDS = 10 * 60
    STARTED_QUIZ_EXPIRATION_SECONDS = 60 * 60

    def __init__(self):
        self.quizes: List[QuizData] = []
        self._read_quizes()
        self.redis_cli = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    def get_quiz_topics(self) -> List[QuizTopic]:
        return [
            QuizTopic(id=q.id, name=q.name) for q in self.quizes
        ]

    def start_quiz(self, request_data: QuizStartRequest) -> UserQuizState:
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
            expires=expires
        )
        self.redis_cli.set(
            f"quiz_{q_state.quiz_code}",
            q_state.to_json(),
            ex=self.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        quiz_players = QuizPlayers(
            players=[
                QuizPlayer(
                    user_token=str(uuid.uuid4()),
                    name=request_data.user_name,
                    user_role=QuizUserRole.COMMANDER
                )
            ]
        )
        self.redis_cli.set(
            f"quiz_players_{q_state.quiz_code}",
            quiz_players.to_json(),
            ex=self.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def join_quiz(self, request_data: QuizJoinRequest) -> UserQuizState:
        if not request_data.user_name:
            raise Exception("User name cannot be empty")
        q_state, quiz_players = self._read_quiz_state(
            request_data.quiz_code)
        if request_data.user_name in {u.name for u in quiz_players.players}:
            raise Exception(f"User name '{request_data.user_name}' is already occupied")
        quiz_players.players.append(
            QuizPlayer(
                user_token=str(uuid.uuid4()),
                name=request_data.user_name,
                user_role=QuizUserRole.PLAYER
            )
        )
        self.redis_cli.set(
            f"quiz_players_{q_state.quiz_code}",
            quiz_players.to_json(),
            ex=self.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[-1],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def get_quiz_status(self, request_data: QuizStatusRequest) -> UserQuizState:
        q_state, quiz_players = self._read_quiz_state(
            request_data.quiz_code)
        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception("User token not found among the quiz users")
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def schedule_quiz(self, request_data: ScheduleQuizRequest) -> UserQuizState:
        q_state, quiz_players = self._read_quiz_state(
            request_data.quiz_code)
        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception(f"User token not found among the quiz users")
        if current_users[0].user_role != QuizUserRole.COMMANDER:
            raise Exception("Current user is not a quiz commander")
        # update the state
        q_state.status = QuizStatusCode.SCHEDULED
        q_state.starts_at = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=request_data.delay_seconds)
        self.redis_cli.set(
            f"quiz_{q_state.quiz_code}",
            q_state.to_json(),
            ex=self.STARTED_QUIZ_EXPIRATION_SECONDS + request_data.delay_seconds
        )
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def _read_quiz_state(self, quiz_code: int) -> Tuple[QuizState, QuizPlayers]:
        json_data = self.redis_cli.get(
            f"quiz_{quiz_code}"
        )
        if not json_data:
            raise Exception(f"Quiz #{quiz_code} not found")
        q_state: QuizState = QuizState.from_json(json_data)
        json_data = self.redis_cli.get(
            f"quiz_players_{quiz_code}"
        )
        quiz_players: QuizPlayers = QuizPlayers.from_json(json_data)
        return q_state, quiz_players

    def _read_quizes(self) -> None:
        quiz_path = settings.quiz_path
        # list directories q01 ...
        for dir_name, dir_path in [
            (o, os.path.join(quiz_path, o)) for o in os.listdir(quiz_path)
                if os.path.isdir(os.path.join(quiz_path, o))]:
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', dir_name):
                continue
            # read "quiz_data.json"
            self.quizes.append(self._read_quiz_from_path(dir_path, dir_name))

    def _read_quiz_by_id(self, quiz_id: str) -> QuizData:
        quiz_path = os.path.join(settings.quiz_path, quiz_id)
        return self._read_quiz_from_path(quiz_path, quiz_id)

    def _read_quiz_from_path(self, quiz_path: str, quiz_id: str) -> QuizData:
        file_path = os.path.join(quiz_path, "quiz_data.json")
        with open(file_path, "r") as file:
            json_data = file.read()
        quiz: QuizData = QuizData.from_json(json_data, infer_missing=True)
        quiz.id = quiz_id
        return quiz


quiz_manager = QuizManager()
