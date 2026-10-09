from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ErroDetalhe(BaseModel):  # type: ignore[misc]
    codigo: str
    mensagem: str
    detalhes: dict[str, Any] | None = None


class ErroResposta(BaseModel):  # type: ignore[misc]
    erro: ErroDetalhe
