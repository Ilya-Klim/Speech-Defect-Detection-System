FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY Backend ./Backend
COPY Tools ./Tools
COPY MLModels/svm_model.pkl ./Backend/data/
COPY MLModels/scaler.pkl ./Backend/data/

EXPOSE 54545
CMD ["uvicorn", "Backend.app.main:app", "--host", "0.0.0.0", "--port", "54545"]