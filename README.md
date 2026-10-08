# Instagram Tracker

Aplicação web para análise e comparação de listas de seguidores e contas seguidas do Instagram a partir de arquivos CSV.

> **Stateless · Privacy-focused · No Instagram API**

## Funcionalidades

* Identifica quem deixou de seguir você
* Identifica novos seguidores
* Identifica quem não segue de volta
* Identifica conexões mútuas
* Detecta contas que alteraram o username
* Exporta os resultados para CSV
* Processa os dados em memória, sem persistência

## Tecnologias

* **Backend:** Python, FastAPI, Pandas
* **Frontend:** HTML, CSS, JavaScript
* **Testes:** Pytest
* **Infra:** Docker

## Privacidade

O projeto não utiliza:

* API ou login do Instagram
* Scraping
* Banco de dados
* Serviços de terceiros
* Armazenamento permanente dos arquivos

Os CSVs são processados em memória e descartados após a análise.

## Execução

```bash
git clone <URL_DO_REPOSITORIO>
cd instagram-tracker

python -m venv .venv
source .venv/bin/activate

pip install -e .
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Acesse `http://127.0.0.1:8000`.

## Documentação

A documentação técnica e as decisões de arquitetura estão disponíveis em [`docs/`](docs/).
