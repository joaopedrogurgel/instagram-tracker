
from pydantic import BaseModel


class PerfilOut(BaseModel):
    user_id: str | None
    username: str
    nome: str | None
    privado: bool | None
    verificado: bool | None
    url: str | None


class RenomeadoOut(BaseModel):
    username_antigo: str
    username_novo: str
    perfil: PerfilOut


class ResumoAnalise(BaseModel):
    total_antigo: int
    total_novo: int
    deixaram_de_seguir: int | None = None
    novos_seguidores: int | None = None
    deixei_de_seguir: int | None = None
    passei_a_seguir: int | None = None
    mantidos: int
    renomeados: int
    houve_mudanca: bool


class AnaliseSeguidores(BaseModel):
    resumo: ResumoAnalise
    deixaram_de_seguir: list[PerfilOut]
    novos_seguidores: list[PerfilOut]
    mantidos: list[PerfilOut]
    renomeados: list[RenomeadoOut]


class AnaliseSeguindo(BaseModel):
    resumo: ResumoAnalise
    deixei_de_seguir: list[PerfilOut]
    passei_a_seguir: list[PerfilOut]
    mantidos: list[PerfilOut]
    renomeados: list[RenomeadoOut]


class ResumoCruzada(BaseModel):
    total_seguidores: int
    total_seguindo: int
    mutuos: int
    nao_retribuem: int
    fas: int


class AnaliseCruzada(BaseModel):
    resumo: ResumoCruzada
    mutuos: list[PerfilOut]
    nao_retribuem: list[PerfilOut]
    fas: list[PerfilOut]


class Metadados(BaseModel):
    tempo_processamento_ms: int
    chave_identificacao: str
    linhas_descartadas: dict[str, int]
    arquivos_ignorados: list[str]
    versao_api: str


class RespostaComparacao(BaseModel):
    analises_executadas: list[str]
    seguidores: AnaliseSeguidores | None
    seguindo: AnaliseSeguindo | None
    cruzada: AnaliseCruzada | None
    metadados: Metadados
