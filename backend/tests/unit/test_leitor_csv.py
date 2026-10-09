import pytest

from backend.app.core.erros import (
    ArquivoVazioError,
    ColunaAusenteError,
    SemDadosValidosError,
    TipoInvalidoError,
)
from backend.app.services.leitor_csv import ler_csv


def test_ler_csv_vazio():
    with pytest.raises(ArquivoVazioError):
        ler_csv("seguidores", "teste.csv", b"")

def test_ler_csv_tipo_invalido():
    with pytest.raises(TipoInvalidoError):
        ler_csv("seguidores", "teste.txt", b"username\nana")

def test_ler_csv_coluna_ausente():
    with pytest.raises(ColunaAusenteError):
        ler_csv("seguidores", "teste.csv", b"nome,idade\nAna,20")

def test_ler_csv_sem_dados():
    with pytest.raises(SemDadosValidosError):
        ler_csv("seguidores", "teste.csv", b"username\n\n\n")

def test_ler_csv_valido():
    csv_bytes = b"User Id,Username,Fullname\n1001,ana,Ana Costa\n1002,joao,\n"
    mapa, descartadas = ler_csv("seguidores", "teste.csv", csv_bytes)
    assert len(mapa) == 2
    assert "1001" in mapa
    assert mapa["1001"].username == "ana"
    assert mapa["1001"].nome == "Ana Costa"
    assert "1002" in mapa
    assert mapa["1002"].username == "joao"
    assert mapa["1002"].nome is None
    assert descartadas == 0

def test_ler_csv_aliases_e_separador():
    csv_bytes = b"userid;handle;is private\n1;ana;yes"
    mapa, _ = ler_csv("seguidores", "teste.csv", csv_bytes)
    assert len(mapa) == 1
    assert "1" in mapa
    assert mapa["1"].username == "ana"
    assert mapa["1"].privado is True
