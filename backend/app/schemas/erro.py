from pydantic import BaseModel


class ErroDetalhe(BaseModel):
    codigo: str
    mensagem: str
    detalhes: dict | None = None

class ErroResposta(BaseModel):
    erro: ErroDetalhe
