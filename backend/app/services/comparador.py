from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Perfil:
    user_id: str | None
    username: str
    nome: str | None = None
    privado: bool | None = None
    verificado: bool | None = None


Mapa = dict[str, Perfil]


def _ordenar(mapa: Mapa, chaves: set[str]) -> list[Perfil]:
    return sorted((mapa[k] for k in chaves), key=lambda p: p.username)


def comparar_par(antigo: Mapa, novo: Mapa) -> dict[str, list[Any]]:
    ka, kn = antigo.keys(), novo.keys()
    comuns = ka & kn
    return {
        "sairam": _ordenar(antigo, ka - kn),
        "entraram": _ordenar(novo, kn - ka),
        "mantidos": _ordenar(novo, comuns),
        "renomeados": [
            {"username_antigo": antigo[k].username, "username_novo": novo[k].username, "perfil": novo[k]}
            for k in sorted(comuns)
            if antigo[k].username != novo[k].username
        ],
    }


def cruzar(seguidores: Mapa, seguindo: Mapa) -> dict[str, list[Perfil]]:
    ks, kg = seguidores.keys(), seguindo.keys()
    return {
        "mutuos": _ordenar(seguidores, ks & kg),
        "nao_retribuem": _ordenar(seguindo, kg - ks),
        "fas": _ordenar(seguidores, ks - kg),
    }
