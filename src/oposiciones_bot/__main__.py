import logging

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from oposiciones_bot.config import get_settings
from oposiciones_bot.domain import load_questions
from oposiciones_bot.infrastructure import Database
from oposiciones_bot.telegram.handlers import (
    process_callback,
    start_command,
)

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = (
        Application.builder().token(get_settings().telegram.token).build()
    )
    application.bot_data["questions"] = load_questions(
        "data/quiz_correct.json"
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(process_callback))

    with Database("data/explanations.db") as db:
        application.bot_data["database"] = db
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
