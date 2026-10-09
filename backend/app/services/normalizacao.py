
import pandas as pd

from backend.app.services.comparador import Mapa, Perfil


def normalizar_username(username: str) -> str:
    if pd.isna(username) or not isinstance(username, str):
        return ""
    return username.strip().lower().lstrip('@')

def normalizar_dataframe(df: pd.DataFrame, usar_user_id: bool) -> tuple[Mapa, int]:
    """
    Normaliza um DataFrame para um Mapa (chave -> Perfil).
    Retorna a tupla (Mapa, linhas_descartadas).
    """
    mapa: Mapa = {}
    linhas_descartadas = 0

    if df.empty:
        return mapa, 0

    # Ensure required columns exist
    if 'username' not in df.columns:
        return mapa, len(df)

    has_user_id = 'user_id' in df.columns
    has_fullname = 'fullname' in df.columns
    has_is_private = 'is private' in df.columns
    has_is_verified = 'is verified' in df.columns

    for _, row in df.iterrows():
        raw_username = row['username']
        username = normalizar_username(raw_username)
        
        if not username:
            linhas_descartadas += 1
            continue

        user_id = str(row['user_id']).strip() if has_user_id and pd.notna(row['user_id']) else None
        
        # Determine the key
        chave = user_id if usar_user_id and user_id else username
        
        if chave in mapa:
            linhas_descartadas += 1
            continue
            
        nome = str(row['fullname']).strip() if has_fullname and pd.notna(row['fullname']) else None
        
        def parse_bool(val: any) -> bool | None:
            if pd.isna(val):
                return None
            val_str = str(val).strip().lower()
            if val_str in ('yes', 'true', '1'):
                return True
            if val_str in ('no', 'false', '0'):
                return False
            return None

        privado = parse_bool(row['is private']) if has_is_private else None
        verificado = parse_bool(row['is verified']) if has_is_verified else None

        mapa[chave] = Perfil(
            user_id=user_id,
            username=username,
            nome=nome,
            privado=privado,
            verificado=verificado
        )

    return mapa, linhas_descartadas
