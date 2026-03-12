Bot de telegram con las preguntas de preparatic, para ejecutarlo necesitas una api key de gemini.

Si no quieres usar la api de pago, puedes usar la api free pero debes desactivar el grounding con google search.

## Ejecución
Usando entornos virtuales
```
python3 -m venv venv
source venv/bin/activate
pip install .
python3 -m oposiciones_bot
```

O usando uv
```
uv run oposiciones_bot
```