import json
import logging
import random
import sqlite3
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import tomllib
from google import genai
from google.genai import types as genai_types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)


class Database:
    def __init__(self, path: str):
        self.path = path

    def __enter__(self) -> "Database":
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cursor.close()
        self.connection.close()

    def init(self) -> None:
        with self.connection:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS explanations (
                    id INTEGER PRIMARY KEY,
                    explanation TEXT
                )
                """
            )

    def save_explanation(self, question_id: str, explanation: str) -> None:
        with self.connection:
            self.cursor.execute(
                "INSERT INTO explanations (id, explanation) VALUES (?, ?)",
                [question_id, explanation],
            )

    def get_explanation(self, question_id: str) -> str:
        with self.connection:
            self.cursor.execute(
                "SELECT explanation FROM explanations WHERE id = ?",
                [question_id],
            )
            result = self.cursor.fetchone()
            return result[0] if result else None


@dataclass
class Question:
    raw: dict
    lines: list[str]
    correct: int

    def as_str(self) -> str:
        return "".join(self.lines)

    def add_line(self, line: str) -> None:
        self.lines.append(line)

    @property
    def options(self) -> list[str]:
        return [chr(65 + idx) for idx in range(len(self.raw["answers"]))]

    def letter(self, idx: int) -> str:
        return chr(65 + idx)


async def augment_question(content: str) -> AsyncGenerator[str, None]:
    async with genai.Client(
        api_key=CONFIG["gemini"]["token_paid"]
        # api_key=CONFIG["gemini"]["token_free_3"]
    ).aio as client:
        async for chunk in await client.models.generate_content_stream(
            # model="gemini-3-flash-preview",
            model="gemini-3.1-flash-lite-preview",
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
        ):
            yield chunk.text


async def explain_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE, pick: str
) -> None:
    cached = DATABASE.get_explanation(pick)
    if cached is None:
        question = format_question(pick)
        draft_id = uuid.uuid4().int & (1 << 64) - 1

        full_text = f"<b>Explicación ({pick})</b>:\n"
        async for chunk in augment_question(
            "".join(question.lines).replace("<b>", "").replace("</b>", "")
        ):
            full_text = f"{full_text}{chunk}"
            await update.effective_message.reply_text_draft(
                draft_id=draft_id, text=full_text, parse_mode=ParseMode.HTML
            )
        DATABASE.save_explanation(pick, full_text)
    else:
        full_text = cached
    await update.effective_message.reply_html(full_text, do_quote=True)


def format_question(pick: str) -> Question:
    raw = DATA_QUIZ[pick]
    correct = raw["correct"]
    text = [
        f"<b>Pregunta ({pick})</b>:\n{raw['title']}\n\n<b>Respuestas</b>:\n"
    ]
    question = Question(raw=raw, lines=text, correct=correct)
    for ans, letter in zip(raw["answers"], question.options):
        question.add_line(f"- {letter}: {ans}\n")
    return question


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_chat.id in CONFIG["telegram"]["allowed_ids"]:
        await update.effective_message.reply_chat_action(ChatAction.TYPING)

        pick = random.choice(list(DATA_QUIZ))
        # pick = "712"

        question = format_question(pick)

        question.add_line(f"\n<b>Estado</b>: {question.raw['status']}\n")
        explanation = None
        if question.raw.get("correct_original"):
            correct_answer = question.letter(question.correct)
            original_answer = question.letter(question.raw["correct_original"])
            question.add_line(
                f"<b>Respuesta PreparaTIC</b>: <span class='tg-spoiler'>"
                f"{original_answer}</span>\n"
            )
            explanation = (
                f"Tras corregir la pregunta con IA, la respuesta es "
                f"{correct_answer}. "
                f"La respuesta de PreparaTIC era: "
                f"{original_answer}\n"
            )
        if question.raw.get("reason"):
            question.add_line(
                f"<b>Razón del estado</b>: <span class='tg-spoiler'>"
                f"{question.raw['reason']}</span>\n"
            )

        message = await update.effective_message.reply_html(question.as_str())
        await message.reply_poll(
            "Respuesta",
            question.options,
            type=Poll.QUIZ,
            correct_option_id=question.correct,
            explanation=explanation,
            do_quote=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Explicar 🤖", callback_data=f"explain_{pick}"
                        ),
                        InlineKeyboardButton(
                            "Siguiente ⏭️",
                            callback_data="next_question",
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
    match query.data:
        case data if data.startswith("explain_"):
            await explain_question(update, context, data.split("_")[1])
        case _:
            await start_command(update, context)


def main() -> None:
    application = (
        Application.builder().token(CONFIG["telegram"]["token_prod"]).build()
    )

    application.add_handler(CommandHandler("start", start_command))
    # application.add_handler(CommandHandler("siguiente", start_command))
    # application.add_handler(CommandHandler("examen", start_command))
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

    with open("quiz_correct.json") as f:
        DATA_QUIZ = json.load(f)

    with Database("explanations.db") as DATABASE:
        main()
