import pandas as pd

from backend.app.services.normalizacao import normalizar_dataframe, normalizar_username


def test_normalizar_username():
    assert normalizar_username("@Ana") == "ana"
    assert normalizar_username(" ana  ") == "ana"
    assert normalizar_username("ANA") == "ana"
    assert normalizar_username(None) == ""
    assert normalizar_username(pd.NA) == ""

def test_normalizar_dataframe_sem_user_id():
    df = pd.DataFrame({
        "username": ["@Ana", " ana  ", "ANA", "joao"],
        "fullname": ["Ana 1", "Ana 2", "Ana 3", "João Silva"]
    })
    # Since all Anas normalize to "ana", only the first should be kept.
    mapa, descartadas = normalizar_dataframe(df, usar_user_id=False)
    
    assert len(mapa) == 2
    assert "ana" in mapa
    assert "joao" in mapa
    assert mapa["ana"].nome == "Ana 1"
    assert descartadas == 2

def test_normalizar_dataframe_com_user_id():
    df = pd.DataFrame({
        "user_id": ["1", "2", "3"],
        "username": ["ana", "joao", ""],
        "is private": ["YES", "no", None]
    })
    mapa, descartadas = normalizar_dataframe(df, usar_user_id=True)
    
    assert len(mapa) == 2
    assert "1" in mapa
    assert "2" in mapa
    assert mapa["1"].privado is True
    assert mapa["2"].privado is False
    assert descartadas == 1
