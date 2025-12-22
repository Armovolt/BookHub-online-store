# Dockerfile
# Багатоетапна збірка для оптимізації розміру образу
FROM python:3.11-slim AS builder

WORKDIR /app

# Встановлюємо системні залежності для компіляції
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файли залежностей
COPY requirements.txt .

# Встановлюємо залежності у віртуальне середовище
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Фінальний етап з легким образом
FROM python:3.11-slim

WORKDIR /app

# Встановлюємо системні залежності для роботи
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо віртуальне середовище з етапу збірки
COPY --from=builder /opt/venv /opt/venv

# Додаємо віртуальне середовище до PATH
ENV PATH="/opt/venv/bin:$PATH"

# Створюємо користувача для безпеки
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Створюємо директорії для даних
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

# Копіюємо код застосунку
COPY --chown=appuser:appuser . .

# Налаштування змінних середовища
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PORT=5000

# Відкриваємо порт
EXPOSE 5000

# Health check (використовуємо wget, який встановлений)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

# Команда запуску
CMD ["python", "app.py"]