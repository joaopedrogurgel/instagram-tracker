# Instagram Tracker

Uma aplicação web stateless de análise de listas de conexões do Instagram.

## Funcionalidades
- Identifica quem deixou de seguir você, novos seguidores e conexões mútuas.
- Análise feita integralmente no servidor em memória.
- Nenhuma integração direta com APIs do Instagram ou serviços de terceiros.
- Zero persistência de dados.

## Execução Local

```bash
# Criar ambiente virtual e instalar dependências
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Rodar a aplicação
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Abra `http://127.0.0.1:8000` no seu navegador.
