"""
FeedFlow - API Principal
Sistema de captura de feedbacks visuais para lojas Shopify
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI(title="FeedFlow API", version="1.0.0")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Registro dos routers

from app.routes.feedback import router as feedback_router
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
# from app.routes.slack_auth import router as slack_auth_router

from app.routes.collection_router import router as collection_router
from app.routes.domain_router import router as domain_router
from app.database.config import init_db
from app.routes.integration_router import router as integration_router


app.include_router(feedback_router)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(integration_router)
# app.include_router(slack_auth_router)

app.include_router(collection_router)
app.include_router(domain_router)

# Logging básico
logging.basicConfig(level=logging.INFO)





