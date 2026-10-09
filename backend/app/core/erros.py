from __future__ import annotations

from typing import Any, Optional


class DomainError(Exception):
    def __init__(self, code: str, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class ArquivoVazioError(DomainError):
    def __init__(self, campo: str):
        super().__init__("ARQUIVO_VAZIO", f"O arquivo '{campo}' está vazio.", {"campo": campo})


class TipoInvalidoError(DomainError):
    def __init__(self, campo: str):
        super().__init__("TIPO_INVALIDO", f"O arquivo '{campo}' não é um CSV. Envie um arquivo com extensão .csv.", {"campo": campo})


class CodificacaoInvalidaError(DomainError):
    def __init__(self, campo: str):
        super().__init__("CODIFICACAO_INVALIDA", f"Não foi possível ler o texto do arquivo '{campo}'. Salve-o novamente como CSV em UTF-8.", {"campo": campo})


class ColunaAusenteError(DomainError):
    def __init__(self, campo: str, colunas: list[str]):
        super().__init__("COLUNA_AUSENTE", f"O arquivo '{campo}' não tem a coluna obrigatória 'Username'. Colunas encontradas: {', '.join(colunas)}.", {"campo": campo, "colunas": colunas})


class SemDadosValidosError(DomainError):
    def __init__(self, campo: str):
        super().__init__("SEM_DADOS_VALIDOS", f"O arquivo '{campo}' não contém nenhum usuário válido.", {"campo": campo})
