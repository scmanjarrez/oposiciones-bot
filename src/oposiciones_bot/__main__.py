import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from oposiciones_bot.config import get_settings
from oposiciones_bot.domain import load_questions
from oposiciones_bot.infrastructure import Database
from oposiciones_bot.telegram.handlers import (
    HELP_COMMANDS,
    help_command,
    next_question_command,
    process_callback,
    start_command,
)

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:  # type: ignore[reportUnknownMemberType]
    await application.bot.set_my_commands(tuple(HELP_COMMANDS.items()))  # type: ignore[reportUnknownMemberType]


async def post_shutdown(application: Application) -> None:  # type: ignore[reportUnknownMemberType]
    await application.bot.delete_my_commands()  # type: ignore[reportUnknownMemberType]


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder()  # type: ignore[reportUnknownMemberType]
        .token(get_settings().telegram.token)
        .post_init(post_init)
        .build()
    )
    application.bot_data["questions"] = load_questions(
        "data/quiz_correct.json"
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("siguiente", next_question_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CallbackQueryHandler(process_callback))

    with Database("data/explanations.db") as db:
        application.bot_data["database"] = db
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
