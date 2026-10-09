from fastapi import Request, status
from fastapi.responses import JSONResponse

from backend.app.core.erros import DomainError


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if exc.code == "ARQUIVO_MUITO_GRANDE":
        status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    elif exc.code in ("COLUNA_AUSENTE", "SEM_DADOS_VALIDOS"):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    return JSONResponse(
        status_code=status_code,
        content={"erro": {"codigo": exc.code, "mensagem": exc.message, "detalhes": exc.details}}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"erro": {"codigo": "ERRO_INTERNO", "mensagem": "Algo deu errado do nosso lado. Tente novamente em instantes."}}
    )
