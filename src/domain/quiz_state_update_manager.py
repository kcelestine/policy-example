import copy
import math
from typing import List, Tuple

from domain.quiz_constants import QuizConstants
from domain.quiz_data import QuizData
from domain.quiz_state import QuizStatusCode, QuizState, QuizResults, QuizResultsPlayer, QuizPlayers
from domain.repository.quiz_state_repository import QuizStateRepository
from domain.time_utils import get_utc_now_time


class QuizStateUpdateManager:
    def __init__(self, state_repo: QuizStateRepository, quizes: List[QuizData]):
        self._state_repo = state_repo
        self._quizes = quizes

    def read_and_update_quiz_state(self, quiz_code: int) -> Tuple[QuizState, QuizPlayers]:
        q_state, quiz_players = self._state_repo.read_quiz_state(quiz_code)
        self._update_quiz_state(q_state)
        return q_state, quiz_players

    def _finish_quiz(self, q_state: QuizState) -> None:
        if q_state == QuizStatusCode.FINISHED:
            return
        q_state.status = QuizStatusCode.FINISHED

        # rank the quiz's users based on their answers
        q_state.updates_in_seconds = QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS
        self._state_repo.set_state(q_state, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)
        players = self._state_repo.read_quiz_players(q_state.quiz_code)
        quiz_data = [q for q in self._quizes if q.id == q_state.id][0]

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
                score = score[0], score[1] + player.answers[i].answer_given_seconds
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
            q_state.quiz_code, results, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)

    def _update_quiz_state(self, quiz_state: QuizState) -> None:
        tm = get_utc_now_time()

        if quiz_state.status == QuizStatusCode.PENDING:
            if quiz_state.expires > tm:
                quiz_state.updates_in_seconds = math.ceil((quiz_state.expires - tm).total_seconds())

        if quiz_state.expires <= tm:
            quiz_state.status = QuizStatusCode.EXPIRED
            self._state_repo.set_state(quiz_state, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)
            return

        if quiz_state.status == QuizStatusCode.SCHEDULED:
            if quiz_state.starts_at > tm:
                quiz_state.updates_in_seconds = math.ceil((quiz_state.starts_at - tm).total_seconds())
            elif quiz_state.starts_at <= tm:
                quiz_state.status = QuizStatusCode.STARTED
                self._state_repo.set_state(quiz_state, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)

        self._check_and_update_running_quiz(quiz_state)

    def _check_and_update_running_quiz(self, q_state: QuizState) -> None:
        # if the quiz is started - check and update the current question
        # if we ran out of questions - stop the quiz
        if q_state.status == QuizStatusCode.STARTED:
            quiz_data = [q for q in self._quizes if q.id == q_state.id][0]
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
                    self._state_repo.set_state(q_state, QuizConstants.STARTED_QUIZ_EXPIRATION_SECONDS)
