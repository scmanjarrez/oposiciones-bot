import random
import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from oposiciones_bot.config import get_settings
from oposiciones_bot.infrastructure import augment_question


async def explain_question(
    update: Update, context: ContextTypes.DEFAULT_TYPE, pick: str
) -> None:
    if update.effective_message is None:
        return

    db = context.bot_data["database"]
    cached = db.get_explanation(pick)
    if cached is None:
        question = context.bot_data["questions"][pick]
        draft_id = uuid.uuid4().int & (1 << 64) - 1

        full_text = f"<b>Explicación ({pick})</b>:\n"
        async for chunk in augment_question(
            question.format_question().replace("<b>", "").replace("</b>", "")
        ):
            full_text = f"{full_text}{chunk}"
            await update.effective_message.reply_text_draft(
                draft_id=draft_id, text=full_text, parse_mode=ParseMode.HTML
            )
        db.save_explanation(pick, full_text)
    else:
        full_text = cached
    await update.effective_message.reply_html(full_text, do_quote=True)


async def start_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_message is None or update.effective_chat is None:
        return

    if update.effective_chat.id in get_settings().telegram.allowed_ids:
        await update.effective_message.reply_chat_action(ChatAction.TYPING)

        questions = context.bot_data["questions"]
        pick = random.choice(list(questions))
        question = questions[pick]

        formatted_question = question.format_message()

        message = await update.effective_message.reply_html(
            formatted_question.message
        )
        await message.reply_poll(
            "Respuesta",
            question.options,
            type=Poll.QUIZ,
            correct_option_id=question.correct,
            explanation=formatted_question.explanation,
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
    if not query or not query.data:
        return

    await query.answer()
    match query.data:
        case data if data.startswith("explain_"):
            await explain_question(update, context, data.split("_")[1])
        case _:
            await start_command(update, context)
