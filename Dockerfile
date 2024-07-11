FROM python:3.11

RUN pip install --upgrade pip  \
    && pip install "poetry==1.6.1"  \
    && poetry config virtualenvs.create false

WORKDIR /auth_app

COPY ["poetry.lock", "pyproject.toml", "./"]

RUN poetry install --no-root --no-interaction --without dev

WORKDIR /app

COPY app .

WORKDIR ..

COPY alembic.ini .

COPY migrations migrations

EXPOSE 8001

CMD ["gunicorn", "-b", "0.0.0.0:8001", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
