# Базовый образ. По умолчанию берется из https://hub.docker.com/_/python
FROM python:3.11-slim

# Поменять рабочую директорию. Если ее нет, создать ее.
WORKDIR /app

# Скопировать из материнской машины в контейнер
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем .env.docker в контейнер как .env для прямой настройки соединений
COPY .env.docker /app/.env

# Create upload directories for images
RUN mkdir -p /app/uploads/events /app/uploads/organizers /app/uploads/coworking

# Запустить команду
CMD ["python", "web_app.py"]