from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from Backend.app.api.v1.api_route import router, init_models
from Tools.logger_config import configure_server_logging

load_dotenv()
configure_server_logging("../logs/")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_models()
    yield

app = FastAPI(
    title="Детектор дефектов речи",
    description="Сервис для анализа произношения скороговорок",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=54545, reload=True)