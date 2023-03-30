import re
from typing import List

import boto3

from domain.quiz_data import QuizData
from domain.repository.quiz_metadata_repository import QuizMetadataRepository
from settings import settings


class QuizMetadataS3Repository(QuizMetadataRepository):
    def __init__(self):
        self.bucket_name = settings.storage_uri
        self.s3 = boto3.client('s3')

    def read_quizes(self) -> List[QuizData]:
        quizes: List[QuizData] = []

        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Delimiter='/')
        for subdir in response.get('CommonPrefixes', []):
            quiz_id = subdir.get('Prefix').rstrip("/")
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', quiz_id):
                continue

            quiz_data = self.s3.get_object(Bucket=self.bucket_name, Key=f"{quiz_id}/quiz_data.json")
            quiz_data_contents = quiz_data['Body'].read()
            quizes.append(self._build_quiz_from_json_string(quiz_id, quiz_data_contents))
        return quizes

    def _build_quiz_from_json_string(self, quiz_id: str, quiz_data_contents: str) -> QuizData:
        quiz: QuizData = QuizData.from_json(quiz_data_contents, infer_missing=True)
        quiz.id = quiz_id
        return quiz
