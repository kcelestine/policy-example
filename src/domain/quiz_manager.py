import datetime
import random
import uuid
from typing import List, Tuple, Optional

from domain.quiz_constants import QuizConstants
from domain.quiz_data import QuizData
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest, \
    StoreAnswerRequest
from domain.quiz_state import QuizState, QuizStatusCode, QuizUserRole, QuizPlayers, QuizPlayer, UserQuizState, \
    QuizPlayerAnswer, QuizResults
from domain.quiz_state_update_manager import QuizStateUpdateManager
from domain.quiz_topic import QuizTopic
from domain.repository.quiz_metadata_fs_repository import QuizMetadataFsRepository
from domain.repository.quiz_metadata_s3_repository import QuizMetadataS3Repository
from domain.repository.quiz_state_repository import QuizStateRepository
from domain.time_utils import get_utc_now_time
from settings import settings


class QuizManager:
    def __init__(self):
        quiz_meta_repo = QuizMetadataS3Repository() if settings.storage_type == "S3" \
            else QuizMetadataFsRepository()
        self._quizes: List[QuizData] = quiz_meta_repo.read_quizes()
        self._state_repo = QuizStateRepository()
        self._state_update_manager = QuizStateUpdateManager(self._state_repo, self._quizes)

    def get_quiz_topics(self) -> List[QuizTopic]:
        return [
            QuizTopic(id=q.id, name=q.name) for q in self._quizes
        ]

    def start_quiz(self, request_data: QuizStartRequest) -> UserQuizState:
        expires = get_utc_now_time() + datetime.timedelta(
            seconds=QuizConstants.PENDING_QUIZ_EXPIRATION_SECONDS)
        quizes = [q for q in self._quizes if q.id == request_data.topic_id]
        if not quizes:
            raise Exception(f"Quiz #{request_data.topic_id} wasn't found out of "
                            f"{self._quizes} quizes")
        quiz = quizes[0]
        q_state = QuizState(
            id=quiz.id,
            name=quiz.name,
            quiz_code=random.randint(0, 100000),
            status=QuizStatusCode.PENDING,
            expires=expires,
            question_seconds=request_data.question_seconds,
            updates_in_seconds=QuizConstants.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        self._state_repo.set_state(q_state, QuizConstants.PENDING_QUIZ_EXPIRATION_SECONDS)
        quiz_players = QuizPlayers(
            players=[
                QuizPlayer(
                    user_token=str(uuid.uuid4()),
                    name=request_data.user_name,
                    user_role=QuizUserRole.COMMANDER,
                    answers=[]
                )
            ]
        )
        self._state_repo.set_quiz_players(
            q_state.quiz_code, quiz_players, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def join_quiz(self, request_data: QuizJoinRequest) -> UserQuizState:
        if not request_data.user_name:
            raise Exception("User name cannot be empty")
        q_state, quiz_players = self._state_update_manager.read_and_update_quiz_state(
            request_data.quiz_code)
        if request_data.user_name in {u.name for u in quiz_players.players}:
            raise Exception(f"User name '{request_data.user_name}' is already occupied")
        quiz_players.players.append(
            QuizPlayer(
                user_token=str(uuid.uuid4()),
                name=request_data.user_name,
                user_role=QuizUserRole.PLAYER,
                answers=[]
            )
        )
        self._state_repo.set_quiz_players(
            q_state.quiz_code, quiz_players, QuizConstants.PENDING_QUIZ_EXPIRATION_SECONDS)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=quiz_players.players[-1],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def get_quiz_status(self, request_data: QuizStatusRequest) -> UserQuizState:
        q_state, quiz_players = self._state_update_manager.read_and_update_quiz_state(
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

    def store_answer(self, request_data: StoreAnswerRequest) -> UserQuizState:
        answer_time = get_utc_now_time()
        q_state, quiz_players = self._state_update_manager.read_and_update_quiz_state(
            request_data.quiz_code)
        if q_state.status != QuizStatusCode.STARTED:
            raise Exception(f"Quiz {request_data.quiz_code} is in {q_state.status} status")

        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception("User token not found among the quiz users")

        if q_state.status == QuizStatusCode.FINISHED:
            raise Exception("Quiz is already finished, no more answers are allowed")

        if request_data.question_index != q_state.cur_question_index[0]:
            raise Exception(f"Current question index is {q_state.cur_question_index}, "
                            f"but the answer was given on the question {request_data.question_index}")

        # initiate answers with empty values
        quiz_data = [q for q in self._quizes if q.id == q_state.id][0]
        if not current_users[0].answers:
            current_users[0].answers = [QuizPlayerAnswer(
                answer=[], answer_given_seconds=q_state.question_seconds)] * len(quiz_data.questions)

        # check how much time passed since question was revealed
        seconds_since_started = (answer_time - q_state.starts_at).total_seconds()
        time_passed = round(seconds_since_started % q_state.question_seconds)
        current_users[0].answers[request_data.question_index] = QuizPlayerAnswer(
            answer=request_data.answer, answer_given_seconds=time_passed)

        # store the updated answers
        self._state_repo.set_quiz_players(
            request_data.quiz_code, quiz_players,
            QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)
        # return the updated state
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

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
        q_state.updates_in_seconds = request_data.delay_seconds

        self._state_repo.set_state(
            q_state, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS + request_data.delay_seconds)
        user_quiz_state = UserQuizState(
            state=q_state,
            user=current_users[0],
            all_user_names=[p.name for p in quiz_players.players]
        )
        return user_quiz_state

    def get_quiz_results(self, quiz_code: int) -> Optional[Tuple[QuizResults, QuizData]]:
        results = self._state_repo.read_quiz_results(quiz_code)
        if not results:
            return None
        quiz_data = [q for q in self._quizes if q.id == results.quiz_id][0]
        return results, quiz_data


quiz_manager = QuizManager()
