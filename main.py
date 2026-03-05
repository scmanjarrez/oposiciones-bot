import json
import logging
import random

import tomllib
from google import genai
from google.genai import types as genai_types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)


async def augment_question(content):
    async with genai.Client(api_key=CONFIG["gemini"]["token"]).aio as client:
        response = await client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=content,
            config=genai_types.GenerateContentConfig(
                system_instruction=(
                    """
Actúa como un tutor experto en oposiciones. Tu única función es analizar preguntas tipo test. Por cada opción de respuesta (A, B, C, D...), debes generar una única línea con el siguiente formato estricto: [Letra]: [Correcta/Incorrecta]: [Breve explicación técnica de máximo 256 caracteres].

Instrucciones críticas:
  - Prohibido incluir introducciones, títulos, negritas fuera del formato, o resúmenes finales.
  - La respuesta debe ser solo el listado de opciones.
  - Sé extremadamente preciso y verifica si la información está desactualizada.
  - Si una opción es 'B y C son correctas', analiza su veracidad en función de las anteriores.
"""
                ),
                tools=[
                    genai_types.Tool(google_search=genai_types.GoogleSearch)
                ],
                thinking_config=genai_types.ThinkingConfig(
                    thinking_level="low"
                ),
            ),
        )
    return response.text


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_chat.id in CONFIG["telegram"]["allowed"]:
        await update.effective_message.reply_chat_action(ChatAction.TYPING)

        pick = random.choice(list(DATA_QUIZ))
        pick = "712"
        question = DATA_QUIZ[pick]
        options = [chr(65 + idx) for idx in range(len(question["answers"]))]
        correct = question["correct"]

        formatted = [
            f"<b>Pregunta ({pick})</b>:\n{question['title']}\n\n"
            f"<b>Respuestas</b>:\n"
        ]
        for ans, letter in zip(question["answers"], options):
            formatted.append(f"- {letter}: {ans}\n")

        augmented = await augment_question(
            "".join(formatted).replace("<b>", "").replace("</b>", "")
        )
        # augmented = "&lt;placeholder&gt;"
        formatted.append(
            f"\n<b>Explicación</b>:\n"
            f"<span class='tg-spoiler'>{augmented}</span>"
        )

        await update.effective_message.reply_html("".join(formatted))
        await update.effective_message.reply_poll(
            "Respuesta",
            options,
            type=Poll.QUIZ,
            correct_option_id=correct,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Siguiente pregunta", callback_data="next_question"
                        ),
                    ]
                ]
            ),
        )


async def process_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    await start_command(update, context)


def main() -> None:
    application = (
        Application.builder().token(CONFIG["telegram"]["token"]).build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(process_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    with open("config.toml", "rb") as f:
        CONFIG = tomllib.load(f)

    with open("quiz_merged.json") as f:
        DATA_QUIZ = json.load(f)

    main()
