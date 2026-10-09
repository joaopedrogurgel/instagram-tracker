from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from typing import Callable, Awaitable

from backend.app.api import rotas_comparar, rotas_saude
from backend.app.config import config
from backend.app.core.erros import DomainError
from backend.app.core.handlers import domain_error_handler, generic_exception_handler
from backend.app.core.limitador import limiter

app = FastAPI(title="Instagram Tracker API", version=config.API_VERSION)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"erro": {"codigo": "ERRO_VALIDACAO", "mensagem": "Requisição inválida. Verifique os campos."}}
    )

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

if config.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def add_security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

app.include_router(rotas_saude.router)
app.include_router(rotas_comparar.router)

# Mount frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
