FROM python:3.13-slim AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:3000"]
