from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
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
    # Aplica segurança em todas as rotas, exceto as do Swagger
    for path in openapi_schema["paths"]:
        if not path.startswith("/docs") and not path.startswith("/openapi") and not path.startswith("/redoc"):
            for method in openapi_schema["paths"][path]:
                openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Rota manual para visualização do Swagger
@app.get("/documentacao", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Documentação Reccredito"
    )
