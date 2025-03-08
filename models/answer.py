from dataclasses import dataclass

@dataclass
class Answer:
    round: int
    model: str
    content: str
    points: int = 0 