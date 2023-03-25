import copy
import datetime
import math
import random
import uuid
from typing import List

from domain.quiz_data import QuizData
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest
from domain.quiz_state import QuizState, QuizStatusCode, QuizUserRole, QuizPlayers, QuizPlayer, UserQuizState
from domain.quiz_topic import QuizTopic
from domain.repository.quiz_metadata_repository import QuizMetadataRepository
from domain.repository.quiz_state_repository import QuizStateRepository
from domain.time_utils import get_utc_now_time


class QuizManager:
    PENDING_QUIZ_EXPIRATION_SECONDS = 10 * 60
    STARTED_QUIZ_EXPIRATION_SECONDS = 60 * 60

    def __init__(self):
        self.quizes: List[QuizData] = QuizMetadataRepository().read_quizes()
        self._state_repo = QuizStateRepository()

    def get_quiz_topics(self) -> List[QuizTopic]:
        return [
            QuizTopic(id=q.id, name=q.name) for q in self.quizes
        ]

    def start_quiz(self, request_data: QuizStartRequest) -> UserQuizState:
        expires = get_utc_now_time() + datetime.timedelta(
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
            question_seconds=request_data.question_seconds
        )
        self._state_repo.set_state(q_state, self.PENDING_QUIZ_EXPIRATION_SECONDS)
        quiz_players = QuizPlayers(
            players=[
                QuizPlayer(
                    user_token=str(uuid.uuid4()),
                    name=request_data.user_name,
                    user_role=QuizUserRole.COMMANDER
                )
            ]
        )
        self._state_repo.set_quiz_players(
            q_state.quiz_code, quiz_players, self.PENDING_QUIZ_EXPIRATION_SECONDS)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def join_quiz(self, request_data: QuizJoinRequest) -> UserQuizState:
        if not request_data.user_name:
            raise Exception("User name cannot be empty")
        q_state, quiz_players = self._state_repo.read_quiz_state(
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
        self._state_repo.set_quiz_players(
            q_state.quiz_code, quiz_players, self.PENDING_QUIZ_EXPIRATION_SECONDS)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[-1],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def get_quiz_status(self, request_data: QuizStatusRequest) -> UserQuizState:
        q_state, quiz_players = self._state_repo.read_quiz_state(
            request_data.quiz_code)
        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception("User token not found among the quiz users")
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        # if the quiz is started - check and update the current question
        # if we ran out of questions - stop the quiz
        if q_state.status == QuizStatusCode.STARTED:
            quiz_data = [q for q in self.quizes if q.id == q_state.id][0]
            seconds_since_started = (get_utc_now_time() - q_state.starts_at).total_seconds()
            question_index = math.floor(seconds_since_started / q_state.question_seconds)
            if question_index >= len(quiz_data.questions):
                self._finish_quiz(q_state)
            else:
                if q_state.cur_question_index[0] != question_index:
                    q_state.cur_question_index = question_index, len(quiz_data.questions)
                    q_state.cur_question = copy.deepcopy(quiz_data.questions[question_index])
                    q_state.cur_question.correct_answers = []
                    self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS)

        return user_quiz_state

    def _finish_quiz(self, q_state: QuizState) -> None:
        q_state.status = QuizStatusCode.FINISHED
        # TODO: rank the quiz's users based on their answers
        self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS)

    def schedule_quiz(self, request_data: ScheduleQuizRequest) -> UserQuizState:
        q_state, quiz_players = self._state_repo.read_quiz_state(
            request_data.quiz_code)
        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception(f"User token not found among the quiz users")
        if current_users[0].user_role != QuizUserRole.COMMANDER:
            raise Exception("Current user is not a quiz commander")
        # update the state
        q_state.status = QuizStatusCode.SCHEDULED
        q_state.starts_at = get_utc_now_time() + datetime.timedelta(
            seconds=request_data.delay_seconds)

        self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS + request_data.delay_seconds)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state


quiz_manager = QuizManager()
