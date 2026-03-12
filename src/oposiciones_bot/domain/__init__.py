"""Domain layer for the oposiciones bot."""

from oposiciones_bot.domain.schemas import (
    FormattedGenAI,
    FormattedMessage,
    Question,
    load_questions,
)

__all__ = ["FormattedMessage", "FormattedGenAI", "Question", "load_questions"]
