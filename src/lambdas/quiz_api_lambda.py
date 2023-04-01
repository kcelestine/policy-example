import json
from typing import Dict, Any

from domain.quiz_manager import quiz_manager
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest, \
    StoreAnswerRequest
from domain.quiz_state import QuizResultsAndData


def get_topics(_request_data: Any) -> str:
    return json.dumps([q.to_dict() for q in quiz_manager.get_quiz_topics()])


def start_quiz(request_data: Dict[str, Any]) -> str:
    return quiz_manager.start_quiz(
        QuizStartRequest.from_dict(request_data)
    ).to_json()


def join_quiz(request_data: Dict[str, Any]) -> str:
    return quiz_manager.join_quiz(
        QuizJoinRequest.from_dict(request_data)).to_json()


def check_status(request_data: Dict[str, Any]) -> str:
    return quiz_manager.get_quiz_status(
        QuizStatusRequest.from_dict(request_data)).to_json()


def schedule_quiz(request_data: Dict[str, Any]) -> str:
    return quiz_manager.schedule_quiz(
        ScheduleQuizRequest.from_dict(request_data)
    ).to_json()


def answer_quiz(request_data: Dict[str, Any]) -> str:
    return quiz_manager.store_answer(
        StoreAnswerRequest.from_dict(request_data)).to_json()


def get_quiz_results(quiz_code: int) -> str:
    results = quiz_manager.get_quiz_results(quiz_code)
    if results:
        results = QuizResultsAndData(quiz_results=results[0], quiz_data=results[1])
        return results.to_json()
    return ""


function_by_request = {
    "quiz-topics": get_topics,
    "quiz-start": start_quiz,
    "quiz-join": join_quiz,
    "quiz-check-status": check_status,
    "quiz-schedule": schedule_quiz,
    "quiz-answer": answer_quiz,
    "quiz-results": get_quiz_results
}


# : LambdaContext = None
def lambda_handler(event: Dict[str, Any], ctx = None) -> Dict[str, Any]:
    event_data = json.loads(event["body"])
    if "requested_operation" not in event_data:
        raise Exception("Thepayload should contain 'requested_operation' field that "
                        "could take one of the following values: " +
                        ", ".join(function_by_request.keys()) +
                        f". The payload was: '{event_data}'")
    processor = function_by_request.get(event_data["requested_operation"])
    if not processor:
        raise Exception(f"The 'requested_operation' field value ({event_data['requested_operation']})"
                        "is incorrect, expected one of the following values: " +
                        ", ".join(function_by_request.keys()))
    response_data = processor(event_data.get("payload"))
    return {
        "statusCode": 200,
        'body': json.dumps(response_data)
    }


if __name__ == "__main__":
    result = lambda_handler({
        "body": json.dumps({
            "requested_operation": "quiz-start",
            "payload": {"topic_id": "d729af45-5ed3-42d0-ac57-d4485b64b067", "user_name": "Alph"}
        })
    })
    print(result)
