from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any

class PerfilOut(BaseModel):
    user_id: Optional[str]
    username: str
    nome: Optional[str]
    privado: Optional[bool]
    verificado: Optional[bool]
    url: Optional[str]

class RenomeadoOut(BaseModel):
    username_antigo: str
    username_novo: str
    perfil: PerfilOut

class ResumoAnalise(BaseModel):
    total_antigo: int
    total_novo: int
    deixaram_de_seguir: Optional[int] = None
    novos_seguidores: Optional[int] = None
    deixei_de_seguir: Optional[int] = None
    passei_a_seguir: Optional[int] = None
    mantidos: int
    renomeados: int
    houve_mudanca: bool

class AnaliseSeguidores(BaseModel):
    resumo: ResumoAnalise
    deixaram_de_seguir: List[PerfilOut]
    novos_seguidores: List[PerfilOut]
    mantidos: List[PerfilOut]
    renomeados: List[RenomeadoOut]

class AnaliseSeguindo(BaseModel):
    resumo: ResumoAnalise
    deixei_de_seguir: List[PerfilOut]
    passei_a_seguir: List[PerfilOut]
    mantidos: List[PerfilOut]
    renomeados: List[RenomeadoOut]

class ResumoCruzada(BaseModel):
    total_seguidores: int
    total_seguindo: int
    mutuos: int
    nao_retribuem: int
    fas: int

class AnaliseCruzada(BaseModel):
    resumo: ResumoCruzada
    mutuos: List[PerfilOut]
    nao_retribuem: List[PerfilOut]
    fas: List[PerfilOut]

class Metadados(BaseModel):
    tempo_processamento_ms: int
    chave_identificacao: str
    linhas_descartadas: Dict[str, int]
    arquivos_ignorados: List[str]
    versao_api: str

class RespostaComparacao(BaseModel):
    analises_executadas: List[str]
    seguidores: Optional[AnaliseSeguidores]
    seguindo: Optional[AnaliseSeguindo]
    cruzada: Optional[AnaliseCruzada]
    metadados: Metadados
