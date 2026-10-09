import io

import pandas as pd

from backend.app.core.erros import (
    ArquivoVazioError,
    CodificacaoInvalidaError,
    ColunaAusenteError,
    SemDadosValidosError,
    TipoInvalidoError,
)
from backend.app.services.comparador import Mapa
from backend.app.services.normalizacao import normalizar_dataframe


def ler_csv(campo: str, nome_arquivo: str, conteudo: bytes, usar_user_id: bool = True) -> tuple[Mapa, int]:
    if not conteudo:
        raise ArquivoVazioError(campo)
        
    if not nome_arquivo.lower().endswith('.csv'):
        raise TipoInvalidoError(campo)
        
    try:
        texto = conteudo.decode('utf-8-sig')
    except UnicodeDecodeError:
        try:
            texto = conteudo.decode('utf-8')
        except UnicodeDecodeError:
            raise CodificacaoInvalidaError(campo)
            
    # Ler apenas a primeira linha para identificar o separador
    try:
        primeira_linha = texto.splitlines()[0]
    except IndexError:
        raise ArquivoVazioError(campo)

    separador = ';' if ';' in primeira_linha else ','
    
    try:
        # Tentar ler o CSV. Pandas levanta erro se estiver malformado
        # Normaliza nomes de colunas: lowercase, strip, substitui espacos por sublinhados
        df = pd.read_csv(io.StringIO(texto), sep=separador, dtype=str)
    except Exception:
        raise CodificacaoInvalidaError(campo)
        
    if df.empty and len(df.columns) == 0:
        raise ArquivoVazioError(campo)

    df.columns = [str(c).strip().lower().replace('_', ' ').replace('-', ' ') for c in df.columns]

    # Aliases
    colunas_map = {
        'username': ['username', 'usuario', 'user', 'handle'],
        'user_id': ['user id', 'userid', 'id'],
        'fullname': ['fullname', 'nome', 'full name'],
        'is private': ['is private', 'privado'],
        'is verified': ['is verified', 'verificado']
    }

    # Rename columns to standard names if matched
    rename_dict = {}
    for standard_col, aliases in colunas_map.items():
        for col in df.columns:
            if col in aliases:
                rename_dict[col] = standard_col
                break

    df = df.rename(columns=rename_dict)

    if 'username' not in df.columns:
        raise ColunaAusenteError(campo, list(df.columns))

    mapa, descartadas = normalizar_dataframe(df, usar_user_id)
    
    if not mapa:
        raise SemDadosValidosError(campo)
        
    return mapa, descartadas
