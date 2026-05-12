FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==1.8.5 && \
    poetry config virtualenvs.create false && \
    poetry install --without linters --no-interaction --no-ansi && \
    rm -rf "$(poetry config cache-dir)/\{cache,artifacts\}"

COPY Client ./Client
COPY Tools ./Tools

ENV PYTHONPATH="/app"
ENV BACKEND_URL="http://backend:54545/api/v1"

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "Client/app_client.py", "--server.port=8501", "--server.address=0.0.0.0"]