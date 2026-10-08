from backend.app.services.comparador import Perfil, comparar_par, cruzar

def test_comparar_par_deixaram_de_seguir():
    antigo = {
        "1": Perfil("1", "a"),
        "2": Perfil("2", "b"),
        "3": Perfil("3", "c"),
    }
    novo = {
        "2": Perfil("2", "b"),
        "3": Perfil("3", "c"),
    }
    resultado = comparar_par(antigo, novo)
    assert len(resultado["sairam"]) == 1
    assert resultado["sairam"][0].username == "a"
    assert len(resultado["entraram"]) == 0
    assert len(resultado["mantidos"]) == 2

def test_comparar_par_novos_seguidores():
    antigo = {
        "1": Perfil("1", "a"),
        "2": Perfil("2", "b"),
    }
    novo = {
        "1": Perfil("1", "a"),
        "2": Perfil("2", "b"),
        "4": Perfil("4", "d"),
    }
    resultado = comparar_par(antigo, novo)
    assert len(resultado["sairam"]) == 0
    assert len(resultado["entraram"]) == 1
    assert resultado["entraram"][0].username == "d"
    assert len(resultado["mantidos"]) == 2

def test_comparar_par_renomeados():
    antigo = {
        "1001": Perfil("1001", "ana"),
    }
    novo = {
        "1001": Perfil("1001", "ana.nova"),
    }
    resultado = comparar_par(antigo, novo)
    assert len(resultado["sairam"]) == 0
    assert len(resultado["entraram"]) == 0
    assert len(resultado["renomeados"]) == 1
    assert resultado["renomeados"][0]["username_antigo"] == "ana"
    assert resultado["renomeados"][0]["username_novo"] == "ana.nova"

def test_cruzar():
    seguidores = {
        "1": Perfil("1", "a"),
        "2": Perfil("2", "b"),
        "3": Perfil("3", "c"),
    }
    seguindo = {
        "2": Perfil("2", "b"),
        "3": Perfil("3", "c"),
        "4": Perfil("4", "d"),
    }
    resultado = cruzar(seguidores, seguindo)
    assert len(resultado["mutuos"]) == 2
    assert len(resultado["nao_retribuem"]) == 1
    assert resultado["nao_retribuem"][0].username == "d"
    assert len(resultado["fas"]) == 1
    assert resultado["fas"][0].username == "a"
