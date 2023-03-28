import copy
import datetime
import math
import random
import uuid
from typing import List, Tuple, Optional

from domain.quiz_data import QuizData
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest, \
    StoreAnswerRequest
from domain.quiz_state import QuizState, QuizStatusCode, QuizUserRole, QuizPlayers, QuizPlayer, UserQuizState, \
    QuizPlayerAnswer, QuizResults, QuizResultsPlayer
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
            question_seconds=request_data.question_seconds,
            updates_in_seconds=self.PENDING_QUIZ_EXPIRATION_SECONDS
        )
        self._state_repo.set_state(q_state, self.PENDING_QUIZ_EXPIRATION_SECONDS)
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
                user_role=QuizUserRole.PLAYER,
                answers=[]
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
        self._check_and_update_running_quiz(q_state)

        return user_quiz_state

    def store_answer(self, request_data: StoreAnswerRequest) -> UserQuizState:
        answer_time = get_utc_now_time()
        q_state, quiz_players = self._state_repo.read_quiz_state(
            request_data.quiz_code)
        if q_state.status != QuizStatusCode.STARTED:
            raise Exception(f"Quiz {request_data.quiz_code} is in {q_state.status} status")

        current_users = [u for u in quiz_players.players if u.user_token == request_data.user_token]
        if not current_users:
            raise Exception("User token not found among the quiz users")

        # update the quiz's status
        self._check_and_update_running_quiz(q_state)

        if q_state.status == QuizStatusCode.FINISHED:
            raise Exception("Quiz is already finished, no more answers are allowed")

        if request_data.question_index != q_state.cur_question_index[0]:
            raise Exception(f"Current question index is {q_state.cur_question_index}, "
                            f"but the answer was given on the question {request_data.question_index}")

        # pad answers from left if some answers were skipped
        if len(current_users[0].answers) < request_data.question_index:
            delta = request_data.question_index - len(current_users[0].answers)
            current_users[0].answers += [QuizPlayerAnswer(answer=[])] * delta
        current_users[0].answers.append(QuizPlayerAnswer(
            answer=request_data.answer, answer_given=answer_time))

        # store the updated answers
        self._state_repo.set_quiz_players(
            request_data.quiz_code, quiz_players, self.STARTED_QUIZ_EXPIRATION_SECONDS)
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

        self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS + request_data.delay_seconds)
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
        quiz_data = [q for q in self.quizes if q.id == results.quiz_id][0]
        return results, quiz_data

    def _check_and_update_running_quiz(self, q_state: QuizState) -> None:
        # if the quiz is started - check and update the current question
        # if we ran out of questions - stop the quiz
        if q_state.status == QuizStatusCode.STARTED:
            quiz_data = [q for q in self.quizes if q.id == q_state.id][0]
            seconds_since_started = (get_utc_now_time() - q_state.starts_at).total_seconds()
            question_index = math.floor(seconds_since_started / q_state.question_seconds)
            # determine interval until next question
            q_state.updates_in_seconds = q_state.question_seconds - \
                                         math.floor(seconds_since_started % q_state.question_seconds)
            if question_index >= len(quiz_data.questions):
                self._finish_quiz(q_state)
            else:
                if q_state.cur_question_index[0] != question_index:
                    q_state.cur_question_index = question_index, len(quiz_data.questions)
                    q_state.cur_question = copy.deepcopy(quiz_data.questions[question_index])
                    q_state.cur_question.correct_answers = []
                    self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS)

    def _finish_quiz(self, q_state: QuizState) -> None:
        if q_state == QuizStatusCode.FINISHED:
            return
        q_state.status = QuizStatusCode.FINISHED

        # rank the quiz's users based on their answers
        self._state_repo.set_state(q_state, self.STARTED_QUIZ_EXPIRATION_SECONDS)
        players = self._state_repo.read_quiz_players(q_state.quiz_code)
        quiz_data = [q for q in self.quizes if q.id == q_state.id][0]
        q_state.updates_in_seconds = self.STARTED_QUIZ_EXPIRATION_SECONDS

        # total number of correct answers / total time spent answering
        players_scores: List[Tuple[int, float]] = [(0, 0)] * len(players.players)
        for i, question in enumerate(quiz_data.questions):
            sorted_answers = sorted(question.correct_answers)

            for player_index, player in enumerate(players.players):
                if i >= len(player.answers):
                    continue
                score = players_scores[player_index]
                player_answers = sorted(player.answers[i].answer)
                if sorted_answers == player_answers:
                    score = score[0] + 1, score[1]
                seconds_since_start = (player.answers[i].answer_given - q_state.starts_at).total_seconds()
                score = score[0], score[1] + seconds_since_start
                players_scores[player_index] = score

        player_score_index = [(i, score) for i, score in enumerate(players_scores)]
        player_score_index.sort(key=lambda item: (item[1][0], -item[1][1]), reverse=True)

        # summarize results
        results = QuizResults(
            quiz_id=quiz_data.id,
            quiz_name=quiz_data.name,
            started_at=q_state.starts_at,
            players=[]
        )
        for index, score in player_score_index:
            player_score = QuizResultsPlayer(
                name=players.players[index].name,
                correct_answers=score[0],
                total_answering_time=score[1],
                answers=players.players[index].answers
            )
            results.players.append(player_score)
        # save the score
        self._state_repo.set_quiz_result(
            q_state.quiz_code, results, self.STARTED_QUIZ_EXPIRATION_SECONDS)


quiz_manager = QuizManager()
