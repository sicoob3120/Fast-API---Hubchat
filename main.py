from fastapi import FastAPI
from app.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API Reccredito",
    description="API segura para acesso ao MongoDB",
    version="1.0.0"
)

app.include_router(router)
