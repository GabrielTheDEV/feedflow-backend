"""
FeedFlow - API Principal
Sistema de captura de feedbacks visuais para lojas Shopify
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import logging

app = FastAPI(title="FeedFlow API", version="1.0.0")


# Custom StaticFiles para desabilitar cache do widget.js 
# -> atualização imediata para os clientes sem precisar limpar cache
class FeedFlowStaticFiles(StaticFiles):
    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)

        if isinstance(response, FileResponse) and response.path.endswith("widget.js"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta arquivos estáticos
app.mount("/static", FeedFlowStaticFiles(directory="app/static"), name="static")


from app.routes.health import router as health_router
from app.routes.collection_router import router as collection_router
from app.routes.domain_router import router as domain_router
from app.routes.integration_router import router as integration_router
from app.routes.report_router import router as report_router


app.include_router(health_router)
app.include_router(integration_router)
app.include_router(report_router)
# app.include_router(slack_auth_router)

app.include_router(collection_router)
app.include_router(domain_router)

# Logging básico
logging.basicConfig(level=logging.INFO)





