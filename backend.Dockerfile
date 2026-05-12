FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==1.8.* && \
    poetry config virtualenvs.create false && \
    poetry install --without client,linters --no-interaction --no-ansi && \
    rm -rf "$(poetry config cache-dir)/\{cache,artifacts\}"

COPY Backend ./Backend
COPY Tools ./Tools


EXPOSE 54545
HEALTHCHECK CMD curl --fail http://localhost:54545/api/v1/health || exit 1

CMD ["uvicorn", "Backend.app.main:app", "--host", "0.0.0.0", "--port", "54545"]