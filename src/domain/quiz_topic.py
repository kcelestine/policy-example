from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class QuizTopic:
    id: str
    name: str
