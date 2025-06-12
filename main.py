from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routes import router
import os

app = FastAPI()

app.include_router(router)

# Personaliza o schema do OpenAPI para forçar o campo correto de API-KEY no Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Reccredito API",
        version="1.0.0",
        description="API Reccredito com segurança via API Key",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-key"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
