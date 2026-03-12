from collections.abc import AsyncGenerator

from google import genai
from google.genai import types

from oposiciones_bot.config import get_settings


async def augment_question(content: str) -> AsyncGenerator[str | None, None]:
    async with genai.Client(api_key=get_settings().gemini.token).aio as client:
        tools = (
            None
            if not get_settings().gemini.google_search_grounding
            else [types.Tool(google_search=types.GoogleSearch())]
        )
        async for chunk in await client.models.generate_content_stream(  # type: ignore[reportUnknownMemberType]
            model=get_settings().gemini.model,
            contents=content,
            config=types.GenerateContentConfig(
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
                tools=tools,
                thinking_config=types.ThinkingConfig(
                    thinking_level=types.ThinkingLevel(
                        get_settings().gemini.thinking_level
                    )
                ),
            ),
        ):
            yield chunk.text
