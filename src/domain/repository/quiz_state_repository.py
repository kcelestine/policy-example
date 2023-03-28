import math
from typing import Tuple, Optional

import redis

from domain.quiz_state import QuizState, QuizPlayers, QuizStatusCode, QuizResults
from domain.time_utils import get_utc_now_time
from settings import settings


class QuizStateRepository:

    def __init__(self):
        self.redis_cli = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    def set_state(self, q_state: QuizState, expiration_seconds: int) -> None:
        self.redis_cli.set(
            f"quiz_{q_state.quiz_code}",
            q_state.to_json(),
            ex=expiration_seconds or None
        )

    def set_quiz_players(self, quiz_code: int, quiz_players: QuizPlayers,
                         expiration_seconds: int) -> None:
        self.redis_cli.set(
            f"quiz_players_{quiz_code}",
            quiz_players.to_json(),
            ex=expiration_seconds
        )

    def set_quiz_result(self, quiz_code: int, results: QuizResults,
                        expiration_seconds: int) -> None:
        self.redis_cli.set(
            f"quiz_results_{quiz_code}",
            results.to_json(),
            ex=expiration_seconds
        )

    def read_quiz_state(self, quiz_code: int) -> Tuple[QuizState, QuizPlayers]:
        json_data = self.redis_cli.get(
            f"quiz_{quiz_code}"
        )
        if not json_data:
            raise Exception(f"Quiz #{quiz_code} not found")
        q_state: QuizState = QuizState.from_json(json_data)

        # update quiz state if necessary, e.g. expire the quiz
        self._update_quiz_state(q_state)
        quiz_players = self.read_quiz_players(quiz_code)
        return q_state, quiz_players

    def read_quiz_players(self, quiz_code: int) -> QuizPlayers:
        json_data = self.redis_cli.get(
            f"quiz_players_{quiz_code}"
        )
        quiz_players: QuizPlayers = QuizPlayers.from_json(json_data)
        return quiz_players

    def read_quiz_results(self, quiz_code: int) -> Optional[QuizResults]:
        json_data = self.redis_cli.get(
            f"quiz_results_{quiz_code}"
        )
        if not json_data:
            return None
        quiz_results: QuizResults = QuizResults.from_json(json_data)
        return quiz_results

    def _update_quiz_state(self, quiz_state: QuizState):
        tm = get_utc_now_time()

        if quiz_state.status == QuizStatusCode.PENDING:
            if quiz_state.expires > tm:
                quiz_state.updates_in_seconds = math.ceil((quiz_state.expires - tm).total_seconds())

        if quiz_state.expires <= tm:
            quiz_state.status = QuizStatusCode.EXPIRED
            self.set_state(quiz_state, 0)
            return

        if quiz_state.status == QuizStatusCode.SCHEDULED:
            if quiz_state.starts_at > tm:
                quiz_state.updates_in_seconds = math.ceil((quiz_state.starts_at - tm).total_seconds())
            elif quiz_state.starts_at <= tm:
                quiz_state.status = QuizStatusCode.STARTED
                self.set_state(quiz_state, 0)
            return
