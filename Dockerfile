FROM python:3.10.10-slim-buster


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "deploy.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
