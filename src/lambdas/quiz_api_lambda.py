from typing import Dict, Any, List

# from aws_lambda_powertools.utilities.typing import LambdaContext

from domain.quiz_manager import quiz_manager
from domain.quiz_requests import QuizStartRequest, QuizJoinRequest, QuizStatusRequest, ScheduleQuizRequest, \
    StoreAnswerRequest


def get_topics(_request_data: Any) -> List[Dict[str, Any]]:
    return [q.to_dict() for q in quiz_manager.get_quiz_topics()]


def start_quiz(request_data: Dict[str, Any]) -> Dict[str, Any]:
    return quiz_manager.start_quiz(
        QuizStartRequest.from_dict(request_data)
    ).to_dict()


def join_quiz(request_data: Dict[str, Any]) -> Dict[str, Any]:
    return quiz_manager.join_quiz(
        QuizJoinRequest.from_dict(request_data)).to_dict()


def check_status(request_data: Dict[str, Any]) -> Dict[str, Any]:
    return quiz_manager.get_quiz_status(
        QuizStatusRequest.from_dict(request_data)).to_dict()


def schedule_quiz(request_data: Dict[str, Any]) -> Dict[str, Any]:
    return quiz_manager.schedule_quiz(
        ScheduleQuizRequest.from_dict(request_data)
    ).to_dict()


def answer_quiz(request_data: Dict[str, Any]) -> Dict[str, Any]:
    return quiz_manager.store_answer(
        StoreAnswerRequest.from_dict(request_data)).to_dict()


def get_quiz_results(quiz_code: int) -> Dict[str, Any]:
    results = quiz_manager.get_quiz_results(quiz_code)
    if results:
        results = {"quiz_results": results[0], "quiz_data": results[1]}
    return results


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
    if "requested_operation" not in event:
        raise Exception("The payload should contain 'requested_operation' field that "
                        "could take one of the following values: "
                        ", ".join(function_by_request.keys()))
    processor = function_by_request.get(event["requested_operation"])
    if not processor:
        raise Exception(f"The 'requested_operation' field value ({event['requested_operation']})"
                        "is incorrect, expected one of the following values: "
                        ", ".join(function_by_request.keys()))
    response_data = processor(event.get("payload"))
    return response_data


if __name__ == "__main__":
    result = lambda_handler({
        "requested_operation": "quiz-topics",
        "payload": {}
    })
    print(result)
