import json
from dataclasses import dataclass
from typing import Any, Literal

GENERAL_TOPICS = range(1, 28)


@dataclass
class FormattedMessage:
    message: str
    explanation: str | None


@dataclass
class FormattedGenAI:
    message: str


@dataclass
class Question:
    id: str
    title: str
    block: str
    topic: str
    year: str
    comments: str | None
    answers: list[str]
    correct: Literal[0, 1, 2, 3]
    status: str
    reason: str | None
    correct_preparatic: int | None

    @property
    def options(self) -> list[str]:
        return [chr(65 + idx) for idx in range(4)]

    def letter(self, idx: int) -> str:
        return chr(65 + idx)

    def format_question(self) -> str:
        message = [
            f"<b>Pregunta ({self.id})</b>:\n{self.title}\n\n"
            f"<b>Respuestas</b>:\n"
        ]
        for idx, answer in enumerate(self.answers):
            message.append(f"- {self.letter(idx)}: {answer}\n")
        return "".join(message)

    def format_message(self) -> FormattedMessage:
        message = [self.format_question()]
        message.append(f"\n<b>Tema</b>: {self.topic} ({self.block})\n")
        message.append(f"<b>Año</b>: {self.year}\n")
        if self.comments:
            message.append(f"<b>Comentarios</b>: {self.comments}\n")

        message.append(f"\n<b>Estado</b>: {self.status}\n")

        explanation = None

        if self.correct_preparatic is not None:
            correct_answer = self.letter(self.correct)
            original_answer = self.letter(self.correct_preparatic)
            message.append(
                f"<b>Respuesta PreparaTIC</b>: <span class='tg-spoiler'>"
                f"{original_answer}</span>\n"
            )
            explanation = (
                f"Tras corregir la pregunta con IA, la respuesta es "
                f"{correct_answer}. "
                f"La respuesta de PreparaTIC era: "
                f"{original_answer}\n"
            )

        if self.reason is not None:
            message.append(
                f"<b>Razón del estado</b>: <span class='tg-spoiler'>"
                f"{self.reason}</span>\n"
            )

        return FormattedMessage(
            message="".join(message), explanation=explanation
        )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Question":
        return Question(
            id=data["id"],
            title=data["title"],
            block=data["block"],
            topic=data["topic"],
            year=data["year"],
            comments=data["comments"],
            answers=data["answers"],
            correct=data["correct"],
            status=data["status"],
            reason=data.get("reason"),
            correct_preparatic=data.get("correct_original"),
        )


@dataclass
class QuestionDatabase:
    questions_by_id: dict[str, Question]
    questions_general: list[Question]
    questions_specific: list[Question]


def load_questions(path: str) -> QuestionDatabase:
    with open(path) as f:
        data = json.load(f)

    questions_all = {k: Question.from_dict(v) for k, v in data.items()}

    questions_general: list[Question] = []
    questions_specific: list[Question] = []
    for question in questions_all.values():
        if int(question.topic) in GENERAL_TOPICS:
            questions_general.append(question)
        else:
            questions_specific.append(question)

    return QuestionDatabase(
        questions_by_id=questions_all,
        questions_general=questions_general,
        questions_specific=questions_specific,
    )
