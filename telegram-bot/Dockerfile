FROM python:3.11-slim

WORKDIR /app

# Copia apenas a pasta do bot
COPY telegram-bot/ /app/

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Inicia o bot
CMD ["python", "bot.py"]
