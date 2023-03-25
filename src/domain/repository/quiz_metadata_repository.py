import os
import re
from typing import List

from domain.quiz_data import QuizData
from settings import settings


class QuizMetadataRepository:
    def read_quizes(self) -> List[QuizData]:
        quizes: List[QuizData] = []
        quiz_path = settings.quiz_path
        # list directories q01 ...
        for dir_name, dir_path in [
            (o, os.path.join(quiz_path, o)) for o in os.listdir(quiz_path)
                if os.path.isdir(os.path.join(quiz_path, o))]:
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', dir_name):
                continue
            # read "quiz_data.json"
            quizes.append(self._read_quiz_from_path(dir_path, dir_name))
        return quizes

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
