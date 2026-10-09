import time

from fastapi import APIRouter, File, Request, UploadFile

from backend.app.config import config
from backend.app.core.erros import DomainError
from backend.app.core.limitador import limiter
from backend.app.schemas.resposta import (
    AnaliseCruzada,
    AnaliseSeguidores,
    AnaliseSeguindo,
    Metadados,
    PerfilOut,
    RenomeadoOut,
    RespostaComparacao,
    ResumoAnalise,
    ResumoCruzada,
)
from backend.app.services.comparador import comparar_par, cruzar
from backend.app.services.leitor_csv import ler_csv

router = APIRouter()

class CombinacaoInvalidaError(DomainError):
    def __init__(self):
        super().__init__("COMBINACAO_INVALIDA", "Envie arquivos que formem uma comparação: dois de seguidores, dois de seguindo, ou um de cada.")

class ArquivoMuitoGrandeError(DomainError):
    def __init__(self, campo: str):
        super().__init__("ARQUIVO_MUITO_GRANDE", f"O arquivo '{campo}' ultrapassa o limite de {config.MAX_FILE_MB} MB.", {"campo": campo})

def formatar_perfil(p) -> PerfilOut:
    url = f"https://www.instagram.com/{p.username}" if p.username else None
    return PerfilOut(
        user_id=p.user_id,
        username=p.username,
        nome=p.nome,
        privado=p.privado,
        verificado=p.verificado,
        url=url
    )

@router.post("/comparar", response_model=RespostaComparacao)
@limiter.limit(config.RATE_LIMIT)
async def comparar(
    request: Request,
    seguidores_antigo: UploadFile | None = File(None),
    seguidores_novo: UploadFile | None = File(None),
    seguindo_antigo: UploadFile | None = File(None),
    seguindo_novo: UploadFile | None = File(None)
):
    start_time = time.time()
    
    arquivos_enviados = {
        "seguidores_antigo": seguidores_antigo,
        "seguidores_novo": seguidores_novo,
        "seguindo_antigo": seguindo_antigo,
        "seguindo_novo": seguindo_novo
    }
    
    arquivos_presentes = {k: v for k, v in arquivos_enviados.items() if v is not None and v.filename}
    
    has_seguidores = "seguidores_antigo" in arquivos_presentes and "seguidores_novo" in arquivos_presentes
    has_seguindo = "seguindo_antigo" in arquivos_presentes and "seguindo_novo" in arquivos_presentes
    has_cruzada = "seguidores_novo" in arquivos_presentes and "seguindo_novo" in arquivos_presentes
    
    if not (has_seguidores or has_seguindo or has_cruzada):
        raise CombinacaoInvalidaError()
        
    mapas = {}
    linhas_descartadas = {}
    max_bytes = config.MAX_FILE_MB * 1024 * 1024
    
    # Process files
    for campo, file in arquivos_presentes.items():
        conteudo = await file.read()
        if len(conteudo) > max_bytes:
            raise ArquivoMuitoGrandeError(campo)
            
        mapa, descartadas = ler_csv(campo, file.filename, conteudo, usar_user_id=True)
        mapas[campo] = mapa
        linhas_descartadas[campo] = descartadas
        
    # Check if we should fallback to username key (if any file is missing user_id for all profiles)
    # Wait, the spec says: if User Id is present in all lines of all compared lists, use it. Otherwise, use Username.
    # To simplify and ensure correctness based on ADR-10, we'll check if any parsed map has elements with None user_id.
    usar_user_id = True
    for mapa in mapas.values():
        for p in mapa.values():
            if not p.user_id:
                usar_user_id = False
                break
        if not usar_user_id:
            break
            
    # If we need to fallback to username, we must re-parse.
    if not usar_user_id:
        mapas = {}
        linhas_descartadas = {}
        for campo, file in arquivos_presentes.items():
            await file.seek(0)
            conteudo = await file.read()
            mapa, descartadas = ler_csv(campo, file.filename, conteudo, usar_user_id=False)
            mapas[campo] = mapa
            linhas_descartadas[campo] = descartadas

    analises_executadas = []
    seguidores_res = None
    seguindo_res = None
    cruzada_res = None
    arquivos_ignorados = []
    
    # Execute analyses
    if has_seguidores:
        analises_executadas.append("seguidores")
        a = mapas["seguidores_antigo"]
        n = mapas["seguidores_novo"]
        res = comparar_par(a, n)
        
        deixaram = [formatar_perfil(p) for p in res["sairam"]]
        novos = [formatar_perfil(p) for p in res["entraram"]]
        mantidos = [formatar_perfil(p) for p in res["mantidos"]]
        renomeados = [
            RenomeadoOut(
                username_antigo=r["username_antigo"], 
                username_novo=r["username_novo"], 
                perfil=formatar_perfil(r["perfil"])
            ) for r in res["renomeados"]
        ]
        
        houve_mudanca = len(deixaram) > 0 or len(novos) > 0 or len(renomeados) > 0
        
        seguidores_res = AnaliseSeguidores(
            resumo=ResumoAnalise(
                total_antigo=len(a), total_novo=len(n),
                deixaram_de_seguir=len(deixaram), novos_seguidores=len(novos),
                mantidos=len(mantidos), renomeados=len(renomeados), houve_mudanca=houve_mudanca
            ),
            deixaram_de_seguir=deixaram,
            novos_seguidores=novos,
            mantidos=mantidos,
            renomeados=renomeados
        )
        
    if has_seguindo:
        analises_executadas.append("seguindo")
        p = mapas["seguindo_antigo"]
        s = mapas["seguindo_novo"]
        res = comparar_par(p, s)
        
        deixei = [formatar_perfil(pf) for pf in res["sairam"]]
        passei = [formatar_perfil(pf) for pf in res["entraram"]]
        mantidos = [formatar_perfil(pf) for pf in res["mantidos"]]
        renomeados = [
            RenomeadoOut(
                username_antigo=r["username_antigo"], 
                username_novo=r["username_novo"], 
                perfil=formatar_perfil(r["perfil"])
            ) for r in res["renomeados"]
        ]
        
        houve_mudanca = len(deixei) > 0 or len(passei) > 0 or len(renomeados) > 0
        
        seguindo_res = AnaliseSeguindo(
            resumo=ResumoAnalise(
                total_antigo=len(p), total_novo=len(s),
                deixei_de_seguir=len(deixei), passei_a_seguir=len(passei),
                mantidos=len(mantidos), renomeados=len(renomeados), houve_mudanca=houve_mudanca
            ),
            deixei_de_seguir=deixei,
            passei_a_seguir=passei,
            mantidos=mantidos,
            renomeados=renomeados
        )
        
    if has_cruzada:
        analises_executadas.append("cruzada")
        n = mapas["seguidores_novo"]
        s = mapas["seguindo_novo"]
        res = cruzar(n, s)
        
        mutuos = [formatar_perfil(pf) for pf in res["mutuos"]]
        nao_retribuem = [formatar_perfil(pf) for pf in res["nao_retribuem"]]
        fas = [formatar_perfil(pf) for pf in res["fas"]]
        
        cruzada_res = AnaliseCruzada(
            resumo=ResumoCruzada(
                total_seguidores=len(n), total_seguindo=len(s),
                mutuos=len(mutuos), nao_retribuem=len(nao_retribuem), fas=len(fas)
            ),
            mutuos=mutuos,
            nao_retribuem=nao_retribuem,
            fas=fas
        )
        
    # Check ignored files
    for campo in arquivos_presentes:
        participa = False
        if campo == "seguidores_antigo" and has_seguidores: participa = True
        if campo == "seguidores_novo" and (has_seguidores or has_cruzada): participa = True
        if campo == "seguindo_antigo" and has_seguindo: participa = True
        if campo == "seguindo_novo" and (has_seguindo or has_cruzada): participa = True
        if not participa:
            arquivos_ignorados.append(campo)

    process_time_ms = int((time.time() - start_time) * 1000)

    metadados = Metadados(
        tempo_processamento_ms=process_time_ms,
        chave_identificacao="user_id" if usar_user_id else "username",
        linhas_descartadas=linhas_descartadas,
        arquivos_ignorados=arquivos_ignorados,
        versao_api=config.API_VERSION
    )

    return RespostaComparacao(
        analises_executadas=analises_executadas,
        seguidores=seguidores_res,
        seguindo=seguindo_res,
        cruzada=cruzada_res,
        metadados=metadados
    )
