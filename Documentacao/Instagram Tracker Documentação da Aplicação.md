# Instagram Tracker: Documentação da Aplicação

*Versão 1.2 · Documento técnico de produto e arquitetura · Status: rascunho para revisão*

## 1. Controle do Documento

| Campo | Valor |
| --- | --- |
| Nome do sistema | Instagram Tracker |
| Tipo | Aplicação web stateless de análise de listas de conexões |
| Stack | HTML/CSS/Vanilla JS · Python · FastAPI · Pandas |
| Público do documento | Desenvolvedores, revisores técnicos, avaliadores acadêmicos |
| Documentos relacionados | Requisitos e Modelagem v1.0 (RF, RNF, RN, contrato OpenAPI) |

### 1.1 Histórico de revisões

| Versão | Data | Descrição |
| --- | --- | --- |
| 0.1 | Out/2026 | Levantamento inicial de requisitos |
| 1.0 | Out/2026 | Consolidação de contexto, arquitetura, engenharia e estrutura do projeto |
| 1.1 | Out/2026 | Autonomia formalizada (sem integração com o Instagram), casos de uso, critérios de aceite, interface, plano de implementação, testes e métricas |
| 1.2 | Out/2026 | Formato real do CSV de exemplo, quatro arquivos (seguidores e seguindo, anterior e atual), três análises (seguidores, seguindo e cruzada), identificação por User Id e redução do arquivo no navegador |

### 1.2 Convenções

Os identificadores **RF** (requisito funcional), **RNF** (requisito não-funcional) e **RN** (regra de negócio) seguem a numeração do documento de Requisitos e Modelagem. Os termos *snapshot*, *unfollower* e *mútuo* estão definidos no Glossário (seção 14).

---

## 2. Introdução

### 2.1 Contexto

O Instagram permite que o usuário solicite uma cópia de suas informações, incluindo as listas de seguidores e de contas seguidas. Essas listas, porém, são exportadas como arquivos brutos, sem nenhuma análise. A plataforma também não informa de forma histórica quem deixou de seguir uma conta, e as ferramentas existentes costumam exigir login com a senha do usuário ou o envio de dados a servidores que os armazenam, o que cria riscos de privacidade e de violação dos termos da plataforma.

O Instagram Tracker nasce dessa lacuna: oferecer a análise das listas de conexões **sem exigir credenciais e sem reter nenhum dado pessoal**.

### 2.2 Declaração do problema

Usuários que desejam entender a evolução de sua base de seguidores não dispõem de uma forma simples, segura e privada de comparar dois momentos no tempo (*snapshots*) e classificar as diferenças em grupos significativos.

### 2.3 Objetivo geral

Desenvolver uma aplicação web que receba arquivos CSV com listas de conexões do Instagram e retorne, de forma rápida e sem persistência de dados, a classificação das diferenças entre eles.

### 2.4 Objetivos específicos

| # | Objetivo | Como é verificado |
| --- | --- | --- |
| OE1 | Identificar mudanças entre dois snapshots de seguidores e entre dois snapshots de contas seguidas | Testes automatizados das regras RN01 e RN02 |
| OE2 | Identificar conexões mútuas e contas que não retribuem o follow | Testes das regras RN04 a RN06 |
| OE3 | Garantir retenção zero de dados pessoais | Revisão de código, auditoria de logs e testes de ausência de escrita em disco |
| OE4 | Entregar resposta em poucos segundos para arquivos volumosos | Testes de carga contra os limites do RNF10 e RNF11 |
| OE5 | Oferecer interface simples, responsiva e acessível | Checklist WCAG 2.1 AA e testes manuais em navegadores-alvo |
| OE6 | Operar de forma autônoma, sem integração com o Instagram nem com serviços externos | Testes CT15 e CT16 e revisão das dependências |

### 2.5 Escopo

**Dentro do escopo**

- Upload de até quatro CSVs: seguidores (anterior e atual) e contas seguidas (anterior e atual), em qualquer combinação que forme ao menos uma análise.
- Normalização, validação e comparação em memória.
- Exibição dos resultados por grupo, com busca e exportação local.

**Fora do escopo (v1.0)**

- Armazenamento de histórico, contas de usuário ou banco de dados.
- Análise de conteúdo (posts, curtidas, comentários).
- Parser nativo do JSON/HTML exportado pelo Instagram (previsto no roadmap).

O sistema não tem nenhuma relação com a API do Instagram. Isso é uma característica de projeto, descrita na seção 2.7, e não um item adiado.

### 2.6 Premissas e restrições

| Tipo | Descrição |
| --- | --- |
| Premissa | O usuário possui os arquivos de suas próprias listas e tem o direito de processá-los. |
| Premissa | Os CSVs seguem o formato do arquivo de exemplo: colunas `User Id`, `Username`, `Fullname`, `Is private`, `Is verified`, `Has default avatar`, `Last story`, `Profile URL` e `Avatar URL`. Só `Username` é obrigatória; `User Id` é recomendada (seção 9.1). |
| Premissa | O sistema não gera nem baixa os arquivos: como o usuário os obtém está fora do sistema (seção 17). |
| Restrição | Arquitetura 100% stateless: proibido persistir conteúdo dos arquivos em qualquer meio. |
| Restrição | Frontend sem frameworks (Vanilla JS) e backend em FastAPI. |
| Restrição | Limite de 25 MB e 500.000 linhas por arquivo enviado ao servidor; o navegador reduz cada arquivo antes do envio (seção 9.1). |

### 2.7 Autonomia do sistema: sem integração com o Instagram

O Instagram Tracker é um sistema **totalmente autônomo**: ele nunca se conecta ao Instagram, a APIs de terceiros ou a qualquer serviço externo para funcionar. Seu único insumo são os arquivos que o próprio usuário fornece.

| Dimensão | Decisão de projeto |
| --- | --- |
| API do Instagram (Graph API, Basic Display) | **Não utilizada.** Nenhuma chamada a endpoints da Meta |
| Login e credenciais | **Inexistentes.** O sistema não pede usuário, senha, token nem cookie de sessão |
| OAuth e permissões de aplicativo | **Não há** aplicativo registrado na Meta, nem revisão de permissões |
| *Scraping* ou automação de navegador | **Proibido** por projeto |
| Serviços de terceiros (analytics, CDN de scripts, fontes remotas, APIs de IA) | **Nenhum.** Todos os ativos são servidos pela própria aplicação |
| Banco de dados, cache, fila, armazenamento de objetos | **Nenhum** (ver RNF01) |
| Fonte dos dados | Arquivos escolhidos pelo usuário em seu dispositivo |
| Rede externa do backend | Nenhuma conexão de saída (*egress*) necessária |
| URLs presentes nos arquivos (Avatar URL, Profile URL) | Ignoradas. Nunca são requisitadas, carregadas ou exibidas, para não gerar chamadas aos servidores do Instagram. O link do perfil é montado a partir do username |

#### Consequências da autonomia

| Aspecto | Efeito |
| --- | --- |
| Conformidade | Sem acesso programático ao Instagram, não há automação que possa violar os termos de uso da plataforma |
| Segurança | Sem credenciais, não há o que vazar; a superfície de ataque se limita ao upload de arquivos |
| Disponibilidade | Mudanças, limites de taxa ou bloqueios da API do Instagram não afetam o sistema |
| Manutenção | Não há integrações para atualizar quando a plataforma altera suas APIs |
| Limitação | O sistema só enxerga o que está nos arquivos. Ele não consegue saber o motivo de um *unfollow* (bloqueio, conta desativada, renomeação) |
| Limitação | A análise é tão atual quanto a exportação do usuário, sem monitoramento em tempo real |

#### Princípios derivados

1. **Dados entram só pelo usuário.** Nada é buscado, apenas recebido.
2. **Cada execução é independente.** Nenhuma requisição depende de outra anterior.
3. **O núcleo funciona sem rede.** A lógica de comparação é uma biblioteca pura, utilizável localmente, inclusive sem o servidor web.
4. **Zero dependência de terceiros em tempo de execução.** O sistema pode ser hospedado em rede isolada.

---

## 3. Partes Interessadas e Personas

| Persona | Perfil | Necessidade principal |
| --- | --- | --- |
| Usuário comum | Pessoa com perfil pessoal, sem conhecimento técnico | Saber quem deixou de segui-la, em poucos cliques |
| Criador de conteúdo | Perfil profissional com milhares de seguidores | Acompanhar a variação da audiência com segurança |
| Social media | Gerencia contas de terceiros, com autorização | Gerar listas exportáveis para relatórios |
| Mantenedor | Desenvolvedor do projeto | Código simples, testável e sem dívida de privacidade |

---

## 4. Visão Geral do Produto

### 4.1 Fluxo de uso

1. O usuário seleciona (ou arrasta) de um a quatro arquivos CSV: seguidores (anterior e atual) e contas seguidas (anterior e atual).
2. O frontend mostra, em tempo real, quais análises os arquivos escolhidos permitem.
3. O navegador reduz cada arquivo, mantendo só `User Id`, `Username` e `Fullname`, e o envia por `fetch`.
4. O backend valida, normaliza e executa em memória todas as análises possíveis.
5. O frontend exibe o resultado de cada análise; o usuário pode buscar, abrir perfis e exportar listas em CSV, tudo no navegador.
6. Ao fechar ou recarregar a página, nenhum dado permanece em lugar algum.

### 4.2 Funcionalidades por grupo

| Análise | Grupo | Fórmula | Arquivos necessários |
| --- | --- | --- | --- |
| Seguidores | Deixaram de seguir | `A − N` | `seguidores_antigo` + `seguidores_novo` |
| Seguidores | Novos seguidores | `N − A` | `seguidores_antigo` + `seguidores_novo` |
| Seguidores | Seguidores mantidos | `A ∩ N` | `seguidores_antigo` + `seguidores_novo` |
| Seguindo | Deixei de seguir | `P − S` | `seguindo_antigo` + `seguindo_novo` |
| Seguindo | Passei a seguir | `S − P` | `seguindo_antigo` + `seguindo_novo` |
| Seguindo | Seguidos mantidos | `P ∩ S` | `seguindo_antigo` + `seguindo_novo` |
| Cruzada | Mútuos | `N ∩ S` | `seguidores_novo` + `seguindo_novo` |
| Cruzada | Não seguem de volta | `S − N` | `seguidores_novo` + `seguindo_novo` |
| Cruzada | Fãs (seguem você, você não segue) | `N − S` | `seguidores_novo` + `seguindo_novo` |
| Seguidores e Seguindo | Renomeados | Mesmo `User Id`, `Username` diferente | Os dois snapshots da análise, com `User Id` |

Com os quatro arquivos, as três análises rodam juntas. Com menos, rodam só as que têm seus arquivos presentes (seção 10).

### 4.3 Casos de uso

O ator único é o **Usuário**, que opera o sistema por conta própria, sem autenticação.

| ID | Caso de uso | Pré-condição | Resultado |
| --- | --- | --- | --- |
| UC01 | Comparar dois snapshots de seguidores | Dois CSVs de seguidores | Deixaram de seguir, novos, mantidos e renomeados |
| UC02 | Comparar dois snapshots de contas seguidas | Dois CSVs de seguindo | Deixei de seguir, passei a seguir, mantidos e renomeados |
| UC03 | Cruzar seguidores e seguidos (quem não segue de volta) | Um CSV de seguidores e um de seguindo, ambos atuais | Mútuos, não seguem de volta e fãs |
| UC04 | Executar as três análises de uma vez | Os quatro CSVs | Seguidores, Seguindo e Cruzada na mesma resposta |
| UC05 | Buscar um perfil nos resultados | Resultado já exibido | Lista filtrada em tempo real |
| UC06 | Exportar um grupo como CSV | Resultado já exibido | Arquivo gerado no navegador |
| UC07 | Corrigir arquivo inválido | Sistema devolveu erro | Usuário entende o problema e reenvia |
| UC08 | Nova análise | Resultado exibido | Estado limpo, nenhum dado anterior mantido |

#### UC01: Comparar dois snapshots de seguidores (detalhado)

| Item | Descrição |
| --- | --- |
| Ator | Usuário |
| Gatilho | Clica em "Comparar" depois de escolher os dois arquivos |
| Pré-condições | Dois arquivos `.csv` selecionados; JavaScript habilitado |
| Pós-condições | Resultado na tela; nenhum dado gravado no servidor |

**Fluxo principal**

1. O usuário seleciona o CSV do snapshot anterior.
2. O usuário seleciona o CSV do snapshot atual.
3. O sistema habilita o botão "Comparar".
4. O usuário clica em "Comparar".
5. O frontend envia os arquivos por `POST /comparar` e exibe o estado de carregamento.
6. O backend valida, normaliza e calcula os conjuntos.
7. O backend devolve o JSON de resultado.
8. O frontend exibe o resumo e as abas de cada grupo.

**Fluxos alternativos e de exceção**

| Passo | Condição | Comportamento |
| --- | --- | --- |
| 2a | O usuário escolhe um arquivo que não é `.csv` | O frontend bloqueia e mostra o aviso antes do envio |
| 2b | O arquivo reduzido passa de 25 MB | O frontend bloqueia o envio e informa o limite |
| 6a | Falta a coluna `username` | O backend responde 422; o frontend exibe a mensagem com as colunas encontradas |
| 6b | Arquivo vazio ou sem linhas válidas | O backend responde 400 ou 422; mensagem indica qual arquivo |
| 6c | Os dois arquivos são idênticos | Resposta 200 com listas vazias e aviso "nenhuma mudança encontrada" |
| 6d | Falha inesperada | Resposta 500; mensagem genérica e opção de tentar de novo |
| 7a | Conexão interrompida | O frontend mostra erro de rede e preserva os arquivos selecionados para novo envio |

---

## 5. Requisitos (Resumo)

Esta seção traz o catálogo completo de requisitos. Os IDs seguem o documento de Requisitos e Modelagem. Nesta versão, RF01, RF02 e RF04 a RF08 foram ampliados para os quatro arquivos e as três análises, e foram acrescentados RF14 a RF18 e RNF19 a RNF24.

### 5.1 Requisitos funcionais

| ID | Requisito | Prioridade | Objetivo |
| --- | --- | --- | --- |
| RF01 | Permitir o upload de até quatro CSVs: seguidores (anterior e atual) e contas seguidas (anterior e atual), cada um opcional | Alta | OE1, OE2 |
| RF02 | Determinar automaticamente, a partir dos arquivos enviados, quais análises são possíveis (seguidores, seguindo, cruzada) e executar todas | Alta | OE1, OE2 |
| RF03 | Validar extensão, codificação, tamanho e estrutura de colunas antes de processar | Alta | OE1 |
| RF04 | Normalizar identificadores (remover `@` e espaços, ignorar maiúsculas, descartar vazios e duplicatas) e identificar cada perfil pelo `User Id` quando presente em todas as linhas, ou pelo `Username` caso contrário | Alta | OE1 |
| RF05 | Identificar quem deixou de seguir o usuário (comparação de dois snapshots de seguidores) | Alta | OE1 |
| RF06 | Identificar novos seguidores | Alta | OE1 |
| RF07 | Identificar conexões mútuas (análise cruzada de seguidores e seguindo atuais) | Média | OE2 |
| RF08 | Identificar contas seguidas que não seguem de volta e seguidores que o usuário não segue (fãs) | Média | OE2 |
| RF09 | Devolver, para cada análise executada, resumo quantitativo e listas completas de cada grupo | Alta | OE1, OE2 |
| RF10 | Enviar os arquivos de forma assíncrona (`fetch` + `FormData`), com estados de carregando, sucesso e erro, sem recarregar a página | Alta | OE5 |
| RF11 | Exibir cada grupo em abas, com contador, busca por nome e link para o perfil | Média | OE5 |
| RF12 | Permitir exportar cada lista como CSV, gerado localmente no navegador | Baixa | OE5 |
| RF13 | Retornar mensagens de erro claras, acionáveis e em português | Alta | OE5 |
| RF14 | Permitir iniciar uma nova análise, limpando arquivos e resultados da tela | Média | OE3 |
| RF15 | Comparar dois snapshots de contas seguidas: deixei de seguir, passei a seguir e mantidos | Alta | OE1 |
| RF16 | Identificar contas renomeadas (mesmo `User Id`, `Username` diferente entre snapshots), sem contá-las como saída ou entrada | Média | OE1 |
| RF17 | Reduzir cada arquivo no navegador antes do envio, mantendo só as colunas necessárias e descartando as demais (principalmente `Avatar URL`) | Alta | OE4, OE3 |
| RF18 | Ignorar as URLs presentes nos arquivos (`Avatar URL`, `Profile URL`) e montar o link do perfil a partir do `Username` validado | Alta | OE3, OE6 |

### 5.2 Requisitos não-funcionais

#### Privacidade, segurança e autonomia

| ID | Requisito |
| --- | --- |
| RNF01 | Retenção zero: nenhum conteúdo dos arquivos ou dos resultados é persistido em banco, cache, fila ou disco além da duração da requisição |
| RNF02 | Processamento em memória (`io.BytesIO`); DataFrames liberados ao fim da requisição; arquivos temporários do servidor apagados ao encerrar |
| RNF03 | Logs sem usernames, conteúdo ou nomes originais dos arquivos; apenas rota, status, duração e tamanho |
| RNF04 | HTTPS (TLS 1.2+) com HSTS |
| RNF05 | Limite de requisições por IP (ex.: 20 req/min), com resposta 429 |
| RNF06 | Renderização com `textContent`, nunca `innerHTML`, contra XSS |
| RNF07 | CORS restrito à origem do frontend; sem cookies, sem autenticação, sem rastreadores |
| RNF08 | `Cache-Control: no-store` em todas as respostas da API |
| RNF19 | Autonomia: nenhuma chamada à API do Instagram, a OAuth, a *scraping* ou a qualquer serviço externo, em nenhum componente |
| RNF20 | O backend não exige acesso de saída à internet para operar |
| RNF21 | Todos os ativos (CSS, JS, fontes, ícones) são servidos localmente, sem CDN nem fontes remotas |
| RNF22 | O sistema não solicita, recebe nem armazena credenciais ou tokens do Instagram |
| RNF23 | Nenhuma URL presente nos arquivos (Avatar URL, Profile URL) é requisitada, carregada ou exibida como imagem; a política de segurança do conteúdo bloqueia origens externas |

#### Desempenho

| ID | Requisito |
| --- | --- |
| RNF09 | Máximo de 25 MB e 500.000 linhas por arquivo enviado ao servidor |
| RNF10 | 2 arquivos de 100.000 linhas processados em até 2 s (p95) no servidor |
| RNF11 | Arquivo de 500.000 linhas em até 8 s (p95); acima do limite, resposta 413 |
| RNF12 | Consumo de memória por requisição de até 512 MB no pior caso, com quatro arquivos de 500.000 linhas processados em sequência |
| RNF13 | Operações de conjunto em complexidade média O(n), sem laços aninhados |
| RNF24 | Quatro arquivos de 100.000 linhas processados em até 4 s (p95) no servidor; a redução no navegador deve diminuir o tamanho do arquivo em mais de 90% no formato de exemplo |

#### Usabilidade e compatibilidade

| ID | Requisito |
| --- | --- |
| RNF14 | Últimas duas versões estáveis de Chrome, Edge, Firefox e Safari (desktop e mobile) |
| RNF15 | Layout responsivo, mobile-first, largura mínima de 360 px |
| RNF16 | Acessibilidade WCAG 2.1 AA: foco visível, rótulos nos campos de arquivo, contraste, erros anunciados por `aria-live` |
| RNF17 | Interface em português (pt-BR) |
| RNF18 | Suporte a *drag and drop* e à seleção tradicional de arquivos |

### 5.3 Rastreabilidade

| Objetivo | Requisitos que o atendem |
| --- | --- |
| OE1 | RF05, RF06, RF15, RF16, RN01, RN02 |
| OE2 | RF07, RF08, RN04–RN06 |
| OE3 | RNF01–RNF03, RNF08 |
| OE4 | RNF09–RNF13 |
| OE5 | RF10, RF11, RF17, RNF14–RNF18 |
| OE6 | RF18, RNF19 a RNF23 |

### 5.4 Critérios de aceite

Cada critério usa o formato *Dado / Quando / Então* e serve de base para os testes de aceitação.

| ID | Requisito | Dado | Quando | Então |
| --- | --- | --- | --- | --- |
| CA01 | RF05 | Seguidores anterior `a, b, c` e atual `b, c` | O usuário compara | `deixaram_de_seguir = [a]` |
| CA02 | RF06 | Seguidores anterior `a, b` e atual `a, b, d` | O usuário compara | `novos_seguidores = [d]` |
| CA03 | RF04 | Arquivos sem `User Id` com `@Ana`, ` ana  ` e `ANA` | O sistema normaliza | As três entradas viram um único `ana` |
| CA04 | RF15 | Seguindo anterior `a, b, c` e atual `b, c, d` | O usuário compara | `deixei_de_seguir = [a]`, `passei_a_seguir = [d]`, `mantidos = [b, c]` |
| CA05 | RF07, RF08 | Seguidores atual `a, b, c` e seguindo atual `b, c, d` | O usuário envia só esses dois | `mutuos = [b, c]`, `nao_retribuem = [d]`, `fas = [a]` |
| CA06 | RN07 | Somente os dois arquivos de seguidores | O usuário compara | `seguindo` e `cruzada` retornam `null` e `analises_executadas = ["seguidores"]` |
| CA07 | RF16 | `User Id` 1001 com username `ana` no anterior e `ana.nova` no atual | O usuário compara | A conta aparece em `renomeados`, não em saídas nem entradas |
| CA08 | RF04 | Arquivos sem a coluna `User Id` e uma conta que trocou de username | O usuário compara | A conta aparece como saída e como entrada, pois a chave é o username |
| CA09 | RN09 | Os dois arquivos têm os mesmos perfis | O usuário compara | Listas de mudança vazias e `houve_mudanca = false` |
| CA10 | RF03 | Arquivo sem a coluna `Username` | O usuário compara | HTTP 422 com `COLUNA_AUSENTE` |
| CA11 | RF02 | Somente `seguidores_antigo`, sem nenhum par | O usuário compara | HTTP 400 com `COMBINACAO_INVALIDA` |
| CA12 | RNF09 | Arquivo reduzido de 26 MB | O usuário envia | Bloqueio no frontend; se chegar ao servidor, HTTP 413 |
| CA13 | RF17 | Arquivo no formato de exemplo (9 colunas) | O usuário o seleciona | O navegador envia só `User Id`, `Username` e `Fullname`, com redução superior a 90% no tamanho |
| CA14 | RF18, RNF23 | Arquivo com `Avatar URL` e `Profile URL`, esta com `javascript:alert(1)` | O resultado é exibido | Nenhuma requisição a essas URLs; o link vem do username |
| CA15 | RNF01 | Qualquer comparação concluída | O sistema responde | Nenhum arquivo ou registro com dados do usuário permanece no servidor |
| CA16 | RF12 | Resultado exibido | O usuário exporta "deixaram de seguir" | CSV gerado no navegador, sem nova requisição à rede |
| CA17 | RNF06 | CSV com username contendo `<script>` | O resultado é exibido | O texto aparece literal, sem execução de código |
| CA18 | RN08 | Entradas em ordem aleatória | O usuário compara | Todas as listas retornam em ordem alfabética |

---

## 6. Regras de Negócio e Fundamentação Teórica

### 6.1 Teoria dos Conjuntos aplicada

Cada lista de conexões é tratada como um **conjunto** de identificadores únicos. Isso é adequado porque a ordem das linhas é irrelevante, duplicatas não devem alterar o resultado e as perguntas do domínio ("quem saiu?", "quem entrou?", "quem está nos dois?") correspondem diretamente a operações de conjuntos.

Sejam os conjuntos de perfis normalizados (regras de identificação na seção 6.4):

| Símbolo | Arquivo | Significado |
| --- | --- | --- |
| `A` | `seguidores_antigo` | Seguidores no snapshot anterior |
| `N` | `seguidores_novo` | Seguidores no snapshot atual |
| `P` | `seguindo_antigo` | Contas seguidas no snapshot anterior |
| `S` | `seguindo_novo` | Contas seguidas no snapshot atual |

| Análise | Operação | Notação | Interpretação no domínio |
| --- | --- | --- | --- |
| Seguidores | Diferença | `A − N` | Seguiam antes e não seguem mais (deixaram de seguir) |
| Seguidores | Diferença | `N − A` | Seguem agora e não seguiam antes (novos seguidores) |
| Seguidores | Interseção | `A ∩ N` | Permaneceram como seguidores |
| Seguindo | Diferença | `P − S` | Você seguia e deixou de seguir |
| Seguindo | Diferença | `S − P` | Você não seguia e passou a seguir |
| Seguindo | Interseção | `P ∩ S` | Você continua seguindo |
| Cruzada | Interseção | `N ∩ S` | Seguem você e você os segue (mútuos) |
| Cruzada | Diferença | `S − N` | Você segue e não seguem você |
| Cruzada | Diferença | `N − S` | Seguem você e você não segue (fãs) |

### 6.2 Complexidade

A construção de um `set` e as operações de diferença e interseção têm custo médio **O(n)** (tabela hash). Isso mantém o tempo de resposta linear no tamanho das listas e evita laços aninhados, que teriam custo O(n²).

### 6.3 Invariantes verificáveis

```text
|N| = |A ∩ N| + |N − A|
|A| = |A ∩ N| + |A − N|
|S| = |P ∩ S| + |S − P|
|P| = |P ∩ S| + |P − S|
|S| = |N ∩ S| + |S − N|
|N| = |N ∩ S| + |N − S|
```

Essas igualdades funcionam como oráculo de teste: qualquer divergência indica defeito na normalização ou na classificação.

### 6.4 Normalização

Identificadores passam por `strip`, remoção de `@` inicial, conversão para minúsculas e descarte de vazios. A conversão para minúsculas se justifica porque nomes de usuário do Instagram não diferenciam maiúsculas de minúsculas.

**Chave de identificação.** Quando todas as linhas válidas das listas comparadas têm `User Id`, cada perfil é identificado por ele, pois o `User Id` não muda quando a pessoa troca de username. Se faltar em qualquer linha de qualquer das listas, a chave passa a ser o `Username` normalizado. A escolha vale para a comparação inteira, e nunca se misturam as duas chaves.

**Contas renomeadas.** Com `User Id`, um perfil presente nos dois snapshots com `Username` diferente é classificado como renomeado: continua em *mantidos* e é listado também em *renomeados*, com o username antigo e o novo. Ele não conta como saída nem como entrada.

**Linhas inválidas e duplicadas.** Linhas sem `Username` são descartadas e contadas. Em caso de chave duplicada, vale a primeira ocorrência. Um username fora do padrão do Instagram (letras, números, ponto e sublinhado, até 30 caracteres) é mantido na análise, mas fica sem link de perfil.

### 6.5 Algoritmo de comparação

O núcleo é uma função pura: recebe mapas de perfis e devolve listas de perfis, sem leitura de disco, rede ou estado global. Isso o torna testável de forma isolada e reutilizável fora do servidor web.

**Pseudocódigo**

```text
FUNÇÃO analisar(arquivos)
    mapas ← para cada arquivo enviado: ler, normalizar e montar o mapa chave → perfil
    chave ← User Id, se todas as listas comparadas o possuem; senão Username

    SE seguidores_antigo e seguidores_novo existem ENTÃO
        seguidores ← comparar_par(A, N)
    SE seguindo_antigo e seguindo_novo existem ENTÃO
        seguindo ← comparar_par(P, S)
    SE seguidores_novo e seguindo_novo existem ENTÃO
        cruzada ← cruzar(N, S)

    SE nenhuma análise foi possível ENTÃO erro COMBINACAO_INVALIDA
    RETORNAR as análises, com nulo para as não calculadas
FIM FUNÇÃO
```

**Implementação de referência** (`services/comparador.py`)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Perfil:
    user_id: str | None
    username: str
    nome: str | None = None

Mapa = dict[str, Perfil]   # chave de identificação -> perfil

def _ordenar(mapa: Mapa, chaves) -> list[Perfil]:
    return sorted((mapa[k] for k in chaves), key=lambda p: p.username)

def comparar_par(antigo: Mapa, novo: Mapa) -> dict:
    ka, kn = antigo.keys(), novo.keys()
    comuns = ka & kn
    return {
        "sairam": _ordenar(antigo, ka - kn),
        "entraram": _ordenar(novo, kn - ka),
        "mantidos": _ordenar(novo, comuns),
        "renomeados": [
            (antigo[k], novo[k]) for k in sorted(comuns)
            if antigo[k].username != novo[k].username
        ],
    }

def cruzar(seguidores: Mapa, seguindo: Mapa) -> dict:
    ks, kg = seguidores.keys(), seguindo.keys()
    return {
        "mutuos": _ordenar(seguidores, ks & kg),
        "nao_retribuem": _ordenar(seguindo, kg - ks),
        "fas": _ordenar(seguidores, ks - kg),
    }
```

A lista "renomeados" só tem elementos quando a chave é o `User Id`; com a chave por username, dois perfis comuns têm sempre o mesmo username. `comparar_par` serve aos seguidores (`sairam` = deixaram de seguir) e aos seguidos (`sairam` = deixei de seguir).

**Orquestração na rota** (`api/rotas_comparar.py`)

| Etapa | Ação | Falha → resposta |
| --- | --- | --- |
| 1 | Verificar que os arquivos enviados formam ao menos uma análise | 400 `COMBINACAO_INVALIDA` |
| 2 | Ler os bytes de cada arquivo com limite de tamanho | 413 `ARQUIVO_MUITO_GRANDE` |
| 3 | Validar extensão e tipo | 400 `TIPO_INVALIDO` |
| 4 | Decodificar (UTF-8 / UTF-8 com BOM) | 400 `CODIFICACAO_INVALIDA` |
| 5 | Ler com Pandas só as colunas usadas e localizar `Username` | 422 `COLUNA_AUSENTE` |
| 6 | Normalizar, escolher a chave e montar o mapa; liberar o DataFrame antes do próximo arquivo | 422 `SEM_DADOS_VALIDOS` |
| 7 | Executar as análises possíveis | 500 `ERRO_INTERNO` |
| 8 | Montar o JSON com análises, resumos e metadados | n/a |

**Análise de complexidade**

| Fase | Custo | Observação |
| --- | --- | --- |
| Leitura do CSV | O(n) | Dominante em tempo e memória |
| Normalização | O(n) | Operações vetorizadas do Pandas |
| Formação dos conjuntos | O(n) médio | Tabela hash |
| Operações de conjunto | O(n) médio | Diferença e interseção |
| Ordenação final | O(k log k) | *k* é o tamanho de cada grupo de saída |

---

## 7. Arquitetura

### 7.1 Visão em camadas

```text
┌─────────────────────────────────────────────┐
│  Navegador (Frontend)                       │
│  HTML/CSS · Vanilla JS · fetch + FormData   │
└───────────────┬─────────────────────────────┘
                │ HTTPS · multipart/form-data
┌───────────────▼─────────────────────────────┐
│  Camada de API (FastAPI)                    │
│  rotas · validação · tratamento de erros    │
├─────────────────────────────────────────────┤
│  Camada de Serviço                          │
│  leitura (Pandas) · normalização · conjuntos│
├─────────────────────────────────────────────┤
│  Memória do processo (efêmera)              │
│  DataFrames e sets descartados ao fim       │
└─────────────────────────────────────────────┘
        (sem banco · sem disco · sem cache)
```

### 7.2 Decisões arquiteturais (ADRs resumidos)

| ADR | Decisão | Justificativa | Consequência |
| --- | --- | --- | --- |
| ADR-01 | Arquitetura stateless, sem banco | Eliminar o risco de vazamento de dados pessoais | Sem histórico entre sessões; o usuário reenvia os arquivos |
| ADR-02 | FastAPI | Tipagem, validação, documentação OpenAPI automática, alto desempenho assíncrono | Dependência de Python 3.11+ |
| ADR-03 | Pandas para leitura e *sets* para comparação | Leitura robusta de CSV (separadores, BOM, tipos) e operações de conjunto O(n) | Pandas é pesado para tarefas triviais, mitigado pelos limites de tamanho |
| ADR-04 | Vanilla JS | Sem *build*, sem dependências, superfície de ataque menor | Mais código manual de interface |
| ADR-05 | Exportação de CSV feita no cliente | Os resultados não voltam ao servidor | Depende de `Blob` e `URL.createObjectURL` |
| ADR-06 | Listas devolvidas ordenadas | Resultados determinísticos e testáveis | Custo O(n log n) na ordenação final |

### 7.3 Fluxo de processamento no backend

```text
requisição → limite de taxa → verificação da combinação de arquivos
   → para cada arquivo: validação de tipo e tamanho → leitura em BytesIO
        → pd.read_csv (só as colunas usadas) → normalização → mapa chave → perfil
   → escolha da chave (User Id ou Username)
   → análises possíveis (seguidores, seguindo, cruzada) → ordenação
   → montagem do JSON → resposta (Cache-Control: no-store) → coleta de lixo dos objetos
```

### 7.4 Atributos de qualidade

| Atributo | Estratégia arquitetural |
| --- | --- |
| Privacidade | Sem persistência, logs sem conteúdo, `no-store`, renderização via `textContent` |
| Desempenho | Operações O(n), limites de tamanho, leitura apenas das colunas necessárias |
| Escalabilidade | Stateless permite escala horizontal atrás de um balanceador, sem sessão compartilhada |
| Manutenibilidade | Separação entre API, serviço e utilitários; funções puras testáveis |
| Testabilidade | Núcleo de comparação sem dependência de HTTP |

### 7.5 Modos de execução autônomos

Como o sistema não depende de nenhum serviço externo, ele roda em qualquer lugar onde haja Python. O próprio FastAPI serve os arquivos estáticos do frontend (`StaticFiles`), o que resulta em um único processo e uma única origem, sem necessidade de CORS em produção.

| Modo | Quem executa | Rede necessária | Indicado para |
| --- | --- | --- | --- |
| **Local** | O próprio usuário, em seu computador | Nenhuma (apenas `localhost`) | Máxima privacidade: os arquivos nunca saem da máquina |
| **Self-hosted** | Equipe ou pessoa, em servidor próprio via Docker | Rede interna ou HTTPS público | Uso compartilhado em organização, sem terceiros |
| **Nuvem** | Provedor de hospedagem (PaaS ou VPS) | HTTPS público | Disponibilizar o serviço ao público em geral |

**Execução local (modo de referência)**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
# abrir http://127.0.0.1:8000 no navegador
```

**Execução com Docker**

```bash
docker build -t instagram-tracker .
docker run --rm -p 8000:8000 instagram-tracker
```

**Decisão arquitetural adicional**

| ADR | Decisão | Justificativa | Consequência |
| --- | --- | --- | --- |
| ADR-07 | Nenhuma integração com a API do Instagram; entrada exclusivamente por arquivos do usuário | Evita credenciais, revisão de apps na Meta, limites de taxa e risco de violar termos de uso | O sistema não consegue obter dados sozinho nem detectar mudanças em tempo real |
| ADR-08 | Frontend servido pelo próprio backend | Um só artefato de implantação, sem CORS e sem CDN | Frontend e backend são versionados e implantados juntos |
| ADR-09 | O navegador reduz cada CSV antes do envio, mantendo só User Id, Username e Fullname | O arquivo de exemplo tem cerca de 600 bytes por linha, 83% deles na coluna Avatar URL. A redução leva a cerca de 43 bytes por linha e evita enviar dados desnecessários | O frontend precisa de um leitor de CSV próprio; quem chamar a API diretamente fica sujeito ao limite de 25 MB do arquivo bruto |
| ADR-10 | Identificar perfis pelo User Id quando disponível, com o Username como alternativa | O User Id não muda quando a pessoa troca de username, o que elimina o falso positivo de unfollower mais comum | Duas chaves possíveis exigem regra clara de escolha por análise e testes dedicados |

---

## 8. Estrutura do Projeto

```text
instagram-tracker/
├── README.md
├── LICENSE
├── pyproject.toml              # dependências e configuração de ferramentas
├── .env.example                # variáveis de ambiente (sem segredos reais)
├── .gitignore
├── Dockerfile
├── docker-compose.yml
│
├── docs/
│   ├── requisitos-e-modelagem.md
│   ├── arquitetura.md
│   ├── openapi.yaml            # contrato exportado
│   └── adr/
│       └── 0001-arquitetura-stateless.md
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # criação do app, middlewares, handlers
│   │   ├── config.py           # limites e variáveis de ambiente
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── rotas_comparar.py   # POST /comparar
│   │   │   └── rotas_saude.py      # GET /saude
│   │   ├── services/
│   │   │   ├── leitor_csv.py       # leitura e validação com Pandas
│   │   │   ├── normalizacao.py     # regra RN00
│   │   │   └── comparador.py       # regras RN01 a RN06
│   │   ├── schemas/
│   │   │   ├── resposta.py         # modelos Pydantic de saída
│   │   │   └── erro.py             # modelo de erro padronizado
│   │   ├── core/
│   │   │   ├── erros.py            # exceções de domínio
│   │   │   ├── handlers.py         # mapeamento exceção → HTTP
│   │   │   └── limitador.py        # limite de requisições
│   │   └── utils/
│   │       └── logging.py          # logs sem dados pessoais
│   └── tests/
│       ├── conftest.py
│       ├── fixtures/               # CSVs sintéticos (nunca dados reais)
│       ├── unit/
│       │   ├── test_normalizacao.py
│       │   ├── test_comparador.py  # inclui invariantes da seção 6.3
│       │   └── test_leitor_csv.py
│       ├── integration/
│       │   └── test_api_comparar.py
│       └── performance/
│           └── test_carga.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── estilos.css
│   └── js/
│       ├── main.js             # inicialização e eventos
│       ├── api.js              # chamadas fetch e redução do CSV
│       ├── ui.js               # renderização (textContent)
│       └── exportar.js         # geração de CSV local
│
└── .github/
    └── workflows/
        └── ci.yml              # lint, testes e verificação de tipos
```

**Notas sobre a estrutura**

- O backend serve `frontend/` como arquivos estáticos, então o projeto gera um único artefato de implantação (ADR-08).
- A pasta `tools/` é opcional e prevista para a v1.1: conterá o conversor local do pacote exportado pelo Instagram para o CSV canônico (seção 17.3), sem acesso à rede.
- `backend/tests/fixtures/` guarda apenas CSVs sintéticos; dados reais nunca entram no repositório.
- Não existem pastas de banco de dados, migrações, credenciais ou integrações externas, o que reflete a autonomia descrita na seção 2.7.

### 8.1 Responsabilidade dos módulos

| Módulo | Responsabilidade | Depende de |
| --- | --- | --- |
| `api/` | Receber requisições, delegar ao serviço, devolver respostas | `services`, `schemas` |
| `services/leitor_csv.py` | Ler bytes, detectar separador, validar colunas | Pandas |
| `services/normalizacao.py` | Transformar uma série em conjunto limpo | Pandas |
| `services/comparador.py` | Aplicar as operações de conjunto | Nenhum (funções puras) |
| `schemas/` | Definir e validar o contrato de saída | Pydantic |
| `core/` | Erros de domínio, handlers e limitação de taxa | FastAPI |
| `frontend/js/` | Interface, redução do CSV, requisições e exportação local | API do navegador |

---

## 9. Modelagem de Dados

### 9.1 Entrada

| Coluna | Obrigatória | Tipo | Uso no sistema | Aliases aceitos |
| --- | --- | --- | --- | --- |
| `Username` | Sim | texto | Identificador exibido; chave quando não há `User Id` | `username`, `usuario`, `user`, `handle` |
| `User Id` | Não (recomendada) | texto numérico | Chave estável; permite detectar renomeações | `user_id`, `userid`, `id` |
| `Fullname` | Não | texto | Nome exibido ao lado do username | `nome`, `full_name` |
| `Is private` | Não | YES ou NO | Selo de conta privada | `is_private` |
| `Is verified` | Não | YES ou NO | Selo de conta verificada | `is_verified` |
| `Has default avatar` | Não | YES ou NO | Ignorada | `has_default_avatar` |
| `Last story` | Não | data | Ignorada | `last_story` |
| `Profile URL` | Não | URL | Ignorada; o link é montado a partir do username | `url`, `link` |
| `Avatar URL` | Não | URL | Ignorada e nunca requisitada | `avatar` |

Codificação UTF-8 (com ou sem BOM), fim de linha LF ou CRLF, separador `,` ou `;` detectado automaticamente e cabeçalho obrigatório. Os nomes de coluna são comparados sem diferenciar maiúsculas e ignorando espaços, sublinhados e hifens: `User Id`, `user_id` e `USERID` são a mesma coluna.

#### Medições do arquivo de exemplo

| Medida | Valor |
| --- | --- |
| Linhas de dados | 230 |
| Tamanho | 138.638 bytes (cerca de 135 KB) |
| Tamanho médio por linha | Cerca de 600 bytes |
| Peso da coluna `Avatar URL` | 83% do arquivo |
| `User Id` e `Username` | 230 valores únicos cada; `User Id` numérico, de 7 a 11 dígitos |
| Usernames | Todos em minúsculas e dentro do padrão do Instagram |
| `Fullname` vazio | 6 linhas |
| `Last story` preenchido | 72 linhas |
| Codificação | UTF-8 com BOM e fim de linha CRLF |

#### Redução no navegador

Antes do envio, o navegador mantém apenas `User Id`, `Username` e `Fullname`. No arquivo de exemplo, isso leva o arquivo de cerca de 139 KB para cerca de 10 KB (redução de 93%) e cada linha de cerca de 600 para cerca de 43 bytes. Com 43 bytes por linha, 500.000 linhas ocupam cerca de 22 MB, dentro do limite de 25 MB. Sem a redução, o mesmo limite comportaria só cerca de 40.000 linhas.

O arquivo de exemplo contém dados reais de terceiros. No repositório do projeto entram apenas arquivos sintéticos com as mesmas colunas.

### 9.2 Saída (`200 OK`)

```json
{
  "analises_executadas": ["seguidores", "seguindo", "cruzada"],
  "seguidores": {
    "resumo": {
      "total_antigo": 1250, "total_novo": 1243,
      "deixaram_de_seguir": 12, "novos_seguidores": 5,
      "mantidos": 1238, "renomeados": 1, "houve_mudanca": true
    },
    "deixaram_de_seguir": [{"user_id": "1001", "username": "ana.costa", "nome": "Ana Costa", "privado": false, "verificado": false, "url": "https://www.instagram.com/ana.costa"}],
    "novos_seguidores": [{"user_id": "1002", "username": "pedro.h", "nome": null, "privado": true, "verificado": false, "url": "https://www.instagram.com/pedro.h"}],
    "mantidos": [{"user_id": "1003", "username": "carla.mendes", "nome": "Carla Mendes", "privado": false, "verificado": false, "url": "https://www.instagram.com/carla.mendes"}],
    "renomeados": [{"user_id": "1003", "username_antigo": "carla.m", "username_novo": "carla.mendes"}]
  },
  "seguindo": {
    "resumo": {
      "total_antigo": 980, "total_novo": 975,
      "deixei_de_seguir": 7, "passei_a_seguir": 2,
      "mantidos": 973, "renomeados": 0, "houve_mudanca": true
    },
    "deixei_de_seguir": [{"user_id": "2001", "username": "loja.exemplo", "nome": "Loja Exemplo", "privado": false, "verificado": true, "url": "https://www.instagram.com/loja.exemplo"}],
    "passei_a_seguir": [{"user_id": "2002", "username": "studio.demo", "nome": "Studio Demo", "privado": false, "verificado": false, "url": "https://www.instagram.com/studio.demo"}],
    "mantidos": [],
    "renomeados": []
  },
  "cruzada": {
    "resumo": {"total_seguidores": 1243, "total_seguindo": 975, "mutuos": 640, "nao_retribuem": 335, "fas": 603},
    "mutuos": [{"user_id": "1003", "username": "carla.mendes", "nome": "Carla Mendes", "privado": false, "verificado": false, "url": "https://www.instagram.com/carla.mendes"}],
    "nao_retribuem": [{"user_id": "2003", "username": "marca.teste", "nome": null, "privado": false, "verificado": true, "url": "https://www.instagram.com/marca.teste"}],
    "fas": [{"user_id": "1002", "username": "pedro.h", "nome": null, "privado": true, "verificado": false, "url": "https://www.instagram.com/pedro.h"}]
  },
  "metadados": {
    "tempo_processamento_ms": 184,
    "chave_identificacao": "user_id",
    "linhas_descartadas": {"seguidores_antigo": 2, "seguidores_novo": 0, "seguindo_antigo": 0, "seguindo_novo": 1},
    "arquivos_ignorados": [],
    "versao_api": "1.1.0"
  }
}
```

As listas do exemplo foram abreviadas. As análises que não puderam ser calculadas por falta de arquivos retornam `null`, e não um objeto com listas vazias (regra RN07); `analises_executadas` diz quais rodaram. Cada perfil traz `user_id` (nulo se o arquivo não tem essa coluna), `username`, `nome`, `privado` e `verificado` (nulos se ausentes) e `url`, sempre montada pelo servidor a partir do `username` e nunca copiada do arquivo (RF18).

### 9.3 Dicionário de dados e ciclo de vida

#### Dicionário dos campos de saída

| Campo | Tipo | Origem (cardinalidade) | Descrição |
| --- | --- | --- | --- |
| `analises_executadas` | lista de texto | derivado | Análises calculadas: `seguidores`, `seguindo` e `cruzada` |
| `seguidores.resumo.total_antigo` | inteiro | card(A) | Seguidores únicos no snapshot anterior |
| `seguidores.resumo.total_novo` | inteiro | card(N) | Seguidores únicos no snapshot atual |
| `seguidores.resumo.deixaram_de_seguir` | inteiro | card(A − N) | Quem deixou de seguir |
| `seguidores.resumo.novos_seguidores` | inteiro | card(N − A) | Novos seguidores |
| `seguidores.resumo.mantidos` | inteiro | card(A ∩ N) | Seguidores que permaneceram |
| `seguindo.resumo.total_antigo` | inteiro | card(P) | Contas seguidas no snapshot anterior |
| `seguindo.resumo.total_novo` | inteiro | card(S) | Contas seguidas no snapshot atual |
| `seguindo.resumo.deixei_de_seguir` | inteiro | card(P − S) | Contas que o usuário deixou de seguir |
| `seguindo.resumo.passei_a_seguir` | inteiro | card(S − P) | Contas que o usuário passou a seguir |
| `seguindo.resumo.mantidos` | inteiro | card(P ∩ S) | Contas que o usuário continua seguindo |
| `*.resumo.renomeados` | inteiro | derivado | Perfis mantidos com username diferente (exige `User Id`) |
| `*.resumo.houve_mudanca` | booleano | derivado | Verdadeiro se houve saída, entrada ou renomeação |
| `cruzada.resumo.total_seguidores` | inteiro | card(N) | Seguidores atuais |
| `cruzada.resumo.total_seguindo` | inteiro | card(S) | Contas seguidas atuais |
| `cruzada.resumo.mutuos` | inteiro | card(N ∩ S) | Conexões recíprocas |
| `cruzada.resumo.nao_retribuem` | inteiro | card(S − N) | Seguidos que não seguem de volta |
| `cruzada.resumo.fas` | inteiro | card(N − S) | Seguidores que o usuário não segue |
| `perfil.user_id` | texto ou nulo | coluna `User Id` | Identificador estável do perfil |
| `perfil.username` | texto | `Username` normalizado | Nome de usuário atual |
| `perfil.nome` | texto ou nulo | `Fullname` | Nome de exibição |
| `perfil.privado`, `perfil.verificado` | booleano ou nulo | `Is private`, `Is verified` | Convertidos de YES e NO |
| `perfil.url` | texto ou nulo | derivado | Link montado do username; nulo se o username está fora do padrão |
| `renomeados[].username_antigo`, `username_novo` | texto | snapshots | Username do mesmo `User Id` em cada snapshot |
| `metadados.tempo_processamento_ms` | inteiro | medido | Duração no servidor, sem o tempo de rede |
| `metadados.chave_identificacao` | texto | derivado | `user_id` ou `username` |
| `metadados.linhas_descartadas` | objeto | normalização | Linhas vazias ou duplicadas removidas, por arquivo |
| `metadados.arquivos_ignorados` | lista de texto | derivado | Arquivos enviados que não participam de nenhuma análise |
| `metadados.versao_api` | texto | configuração | Versão semântica da API |

#### Ciclo de vida da informação

| Fase | Onde fica o dado | Duração | Descarte |
| --- | --- | --- | --- |
| 1. Seleção | Memória do navegador (objeto `File`) | Até o envio ou a recarga da página | Ao fechar ou recarregar a aba |
| 2. Redução | Memória do navegador; colunas desnecessárias são descartadas | Poucos segundos | Ao terminar o envio |
| 3. Transmissão | Corpo da requisição HTTPS | Milissegundos a segundos | Fim da requisição |
| 4. Processamento | Bytes, DataFrames e mapas na memória do processo | Duração da requisição | Coleta de lixo ao retornar da rota |
| 5. Resposta | Corpo da resposta HTTPS | Milissegundos | Fim da requisição |
| 6. Exibição | Memória e DOM do navegador | Enquanto a página estiver aberta | Ao fechar, recarregar ou "Nova análise" |
| 7. Exportação | Arquivo salvo pelo usuário | Controlado pelo usuário | Fora do controle do sistema |

Em nenhuma fase o dado passa por disco, banco, log, cache ou serviço de terceiros.

---

## 10. Contrato da API (Síntese)

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/comparar` | Recebe até quatro CSVs e executa todas as análises possíveis |
| `GET` | `/saude` | Verificação de disponibilidade, sem dados de usuário |

**Parâmetros de `POST /comparar`** (`multipart/form-data`; cada arquivo é opcional por si só)

| Parâmetro | Conteúdo | Participa de |
| --- | --- | --- |
| `seguidores_antigo` | CSV de seguidores, snapshot anterior | Análise de seguidores |
| `seguidores_novo` | CSV de seguidores, snapshot atual | Análise de seguidores e análise cruzada |
| `seguindo_antigo` | CSV de contas seguidas, snapshot anterior | Análise de seguindo |
| `seguindo_novo` | CSV de contas seguidas, snapshot atual | Análise de seguindo e análise cruzada |

**Combinações e resultado**

| Arquivos enviados | Análises executadas |
| --- | --- |
| `seguidores_antigo` + `seguidores_novo` | Seguidores |
| `seguindo_antigo` + `seguindo_novo` | Seguindo |
| `seguidores_novo` + `seguindo_novo` | Cruzada |
| Os quatro arquivos | Seguidores, Seguindo e Cruzada |
| Outras combinações | Cada análise cujos arquivos estejam presentes; arquivos que não participam de nenhuma ficam em `metadados.arquivos_ignorados` |
| Nenhuma análise possível (ex.: um único arquivo) | Erro 400 `COMBINACAO_INVALIDA` |

| HTTP | Situação | Código interno |
| --- | --- | --- |
| 200 | Pelo menos uma análise concluída | n/a |
| 400 | Combinação de arquivos sem nenhuma análise, arquivo vazio, tipo ou codificação inválidos | `COMBINACAO_INVALIDA`, `ARQUIVO_VAZIO`, `TIPO_INVALIDO`, `CODIFICACAO_INVALIDA` |
| 413 | Arquivo acima de 25 MB ou 500 mil linhas | `ARQUIVO_MUITO_GRANDE` |
| 422 | CSV legível, porém sem coluna `Username` ou sem dados válidos | `COLUNA_AUSENTE`, `SEM_DADOS_VALIDOS` |
| 429 | Limite de requisições excedido | `LIMITE_EXCEDIDO` |
| 500 | Falha inesperada, sem detalhes internos | `ERRO_INTERNO` |

O FastAPI responde 422 por padrão a erros de formulário. Para manter o contrato, um `exception_handler` para `RequestValidationError` converte campos ausentes em 400.

### 10.1 Catálogo de mensagens de erro

As mensagens são escritas para o usuário final: dizem o que houve e o que fazer. Nunca incluem nomes de usuário, trechos do arquivo ou detalhes internos do servidor.

| Código interno | HTTP | Mensagem exibida (pt-BR) | Ação sugerida |
| --- | --- | --- | --- |
| `COMBINACAO_INVALIDA` | 400 | Envie arquivos que formem uma comparação: dois de seguidores, dois de seguindo, ou um de seguidores e um de seguindo. | Escolher os arquivos que faltam |
| `ARQUIVO_VAZIO` | 400 | O arquivo "{campo}" está vazio. | Conferir se o arquivo certo foi escolhido |
| `TIPO_INVALIDO` | 400 | O arquivo "{campo}" não é um CSV. Envie um arquivo com extensão .csv. | Converter ou escolher outro arquivo |
| `CODIFICACAO_INVALIDA` | 400 | Não foi possível ler o texto do arquivo "{campo}". Salve-o novamente como CSV em UTF-8. | Reexportar em UTF-8 |
| `ARQUIVO_MUITO_GRANDE` | 413 | O arquivo "{campo}" ultrapassa o limite de 25 MB. | Reduzir ou dividir o arquivo |
| `COLUNA_AUSENTE` | 422 | O arquivo "{campo}" não tem a coluna obrigatória "Username". Colunas encontradas: {colunas}. | Conferir o cabeçalho do arquivo |
| `SEM_DADOS_VALIDOS` | 422 | O arquivo "{campo}" não contém nenhum usuário válido. | Conferir o conteúdo do arquivo |
| `LIMITE_EXCEDIDO` | 429 | Muitas tentativas em pouco tempo. Aguarde um minuto e tente de novo. | Esperar e reenviar |
| `ERRO_INTERNO` | 500 | Algo deu errado do nosso lado. Tente novamente em instantes. | Tentar de novo |

Os campos `{campo}` e `{colunas}` recebem apenas o **nome do parâmetro** da API (por exemplo, `seguidores_novo`) e os **nomes das colunas do cabeçalho**, nunca valores de dados.

#### Cabeçalhos de resposta obrigatórios

| Cabeçalho | Valor | Objetivo |
| --- | --- | --- |
| `Cache-Control` | `no-store` | Impedir cache de dados pessoais |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Forçar HTTPS |
| `X-Content-Type-Options` | `nosniff` | Evitar interpretação indevida de tipo |
| `Content-Security-Policy` | `default-src 'self'` | Bloquear carregamento de qualquer origem externa |
| `Referrer-Policy` | `no-referrer` | Não vazar a origem para terceiros |

---

## 11. Engenharia de Software

### 11.1 Princípios de projeto

| Princípio | Aplicação |
| --- | --- |
| Separação de responsabilidades | API, serviço e esquemas em camadas distintas |
| Funções puras no núcleo | `comparador.py` não faz I/O, o que facilita testes |
| *Fail fast* | Validação de tipo e tamanho antes de qualquer processamento |
| Privacidade por padrão | Nenhum dado é gravado, e os logs só guardam metadados técnicos |
| Contrato primeiro | O OpenAPI é a fonte de verdade entre frontend e backend |

### 11.2 Estratégia de testes

| Nível | Ferramenta | Foco |
| --- | --- | --- |
| Unitário | `pytest` | Normalização, classificação e invariantes (seção 6.3) |
| Propriedade | `hypothesis` | Geração aleatória de conjuntos para validar as invariantes |
| Integração | `pytest` + `TestClient` | Cada código HTTP do contrato, com CSVs sintéticos |
| Desempenho | `locust` ou script dedicado | Metas RNF10 e RNF11, memória conforme RNF12 |
| Privacidade | Teste dedicado | Ausência de escrita em disco e de dados nos logs |
| Interface | Manual + Lighthouse | WCAG 2.1 AA e compatibilidade de navegadores |

Os dados de teste devem ser **sintéticos**. Dados reais de pessoas não devem entrar no repositório.

### 11.3 Qualidade de código

| Ferramenta | Finalidade |
| --- | --- |
| `ruff` | Lint e formatação |
| `mypy` | Verificação estática de tipos |
| `pytest-cov` | Cobertura (meta ≥ 85% no núcleo de serviços) |
| `pre-commit` | Execução local das verificações antes do commit |

### 11.4 Integração e entrega contínuas

```text
push/PR → ruff → mypy → pytest (unit + integração) → cobertura
        → build da imagem Docker → varredura de dependências
        → deploy (somente na branch principal)
```

### 11.5 Implantação e operação

| Item | Definição |
| --- | --- |
| Empacotamento | Imagem Docker com `uvicorn` |
| Configuração | Variáveis de ambiente (limites, origem CORS, taxa de requisições) |
| Escala | Horizontal, sem estado compartilhado |
| Observabilidade | Métricas de latência, status e tamanho, sem conteúdo de usuário |
| Transporte | HTTPS obrigatório com HSTS |

### 11.6 Estratégia de versionamento

Versionamento semântico (`MAJOR.MINOR.PATCH`) para a API, com mudanças incompatíveis exigindo novo prefixo de rota (`/v2/comparar`). Fluxo de branches baseado em *trunk* com *pull requests* revisados.

### 11.7 Casos de teste

| ID | Nível | Cenário | Resultado esperado |
| --- | --- | --- | --- |
| CT01 | Unitário | Normalizar `@Ana`, `ana`, `ANA` | Conjunto com um único elemento `ana` |
| CT02 | Unitário | Coluna com vazios e `NaN` | Valores descartados e contados em `linhas_descartadas` |
| CT03 | Unitário | `comparar_par` com listas iguais | Listas de saída e de entrada vazias |
| CT04 | Unitário | Montar o resultado sem os arquivos de seguindo | `seguindo` e `cruzada` nulos |
| CT05 | Propriedade | Conjuntos aleatórios A, N, P e S | As seis invariantes da seção 6.3 sempre verdadeiras |
| CT06 | Unitário | CSV com separador `;` e BOM | Leitura correta da coluna `Username` |
| CT07 | Unitário | Cabeçalho do arquivo de exemplo (`User Id`, `Username`, BOM, CRLF) e alias `usuario` | Colunas reconhecidas |
| CT08 | Integração | `POST /comparar` com os quatro arquivos válidos | 200 com as três análises, conforme o schema |
| CT09 | Integração | `POST /comparar` só com `seguidores_antigo` | 400 `COMBINACAO_INVALIDA` |
| CT10 | Integração | Arquivo `.txt` | 400 `TIPO_INVALIDO` |
| CT11 | Integração | CSV sem coluna `Username` | 422 `COLUNA_AUSENTE` |
| CT12 | Integração | Arquivo acima de 25 MB | 413 `ARQUIVO_MUITO_GRANDE` |
| CT13 | Integração | 21 requisições em um minuto do mesmo IP | A 21ª retorna 429 |
| CT14 | Privacidade | Executar uma comparação e inspecionar o disco e os logs | Nenhum arquivo novo e nenhum username nos logs |
| CT15 | Autonomia | Executar a suíte com a rede de saída bloqueada | Todos os testes passam |
| CT16 | Autonomia | Varredura estática por URLs e hosts externos no frontend | Nenhuma referência a domínio externo |
| CT17 | Desempenho | Dois arquivos de 100.000 linhas | Resposta em até 2 s (p95) |
| CT18 | Segurança | Username com `<script>alert(1)</script>` | Texto exibido literalmente |
| CT19 | Segurança | Exportar username iniciado por `=` | Valor prefixado com apóstrofo no CSV |
| CT20 | Integração | Dois arquivos de seguindo (anterior e atual) | `deixei_de_seguir`, `passei_a_seguir` e `mantidos` corretos |
| CT21 | Integração | Um arquivo de seguidores e um de seguindo | `mutuos`, `nao_retribuem` e `fas` corretos |
| CT22 | Unitário | Mesmo `User Id` com usernames diferentes | Perfil em `renomeados`, fora de saídas e entradas |
| CT23 | Unitário | Um arquivo sem `User Id` ou com `User Id` vazio em algumas linhas | Chave por username para toda a comparação |
| CT24 | Segurança | Arquivo com `Avatar URL` e `Profile URL` (inclusive `javascript:`) | Nenhuma requisição a essas URLs; link montado do username |
| CT25 | Interface | Selecionar o arquivo de exemplo de 9 colunas | Envio com 3 colunas e redução superior a 90% |
| CT26 | Desempenho | Quatro arquivos de 100.000 linhas | Resposta em até 4 s (p95) |

### 11.8 Configuração por variáveis de ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `MAX_FILE_MB` | `25` | Tamanho máximo por arquivo enviado ao servidor |
| `MAX_ROWS` | `500000` | Máximo de linhas por arquivo |
| `RATE_LIMIT` | `20/minute` | Limite de requisições por IP |
| `ALLOWED_ORIGINS` | vazio | Origens CORS permitidas (vazio quando o frontend é servido pelo backend) |
| `LOG_LEVEL` | `INFO` | Nível de log (nunca registra dados de usuário) |
| `API_VERSION` | `1.1.0` | Versão exposta nos metadados |

Nenhuma variável guarda segredo, chave de API ou credencial, porque o sistema não possui nenhum.

### 11.9 Dependências

| Pacote | Uso | Ambiente |
| --- | --- | --- |
| `fastapi` | Framework da API | Produção |
| `uvicorn` | Servidor ASGI | Produção |
| `python-multipart` | Leitura de `multipart/form-data` | Produção |
| `pandas` | Leitura de CSV e normalização | Produção |
| `pydantic` | Schemas de resposta | Produção |
| `slowapi` | Limite de requisições | Produção |
| `pytest`, `httpx` | Testes unitários e de integração | Desenvolvimento |
| `hypothesis` | Testes de propriedade | Desenvolvimento |
| `ruff`, `mypy` | Lint e tipagem | Desenvolvimento |

O frontend não possui dependências: nenhuma biblioteca JavaScript, nenhum *bundler* e nenhum pacote npm. As versões exatas ficam fixadas em `pyproject.toml` e devem ser revisadas antes de cada release.

---

## 12. Segurança, Privacidade e Conformidade

### 12.1 Modelo de ameaças (resumo)

| Ameaça | Vetor | Mitigação |
| --- | --- | --- |
| Vazamento de dados | Persistência acidental, logs, cache | Retenção zero, `no-store`, logs sanitizados, revisão de código |
| XSS | Nome de usuário malicioso no CSV | Renderização com `textContent`, CSP restritiva |
| Negação de serviço | Arquivos enormes ou muitas requisições | Limites de tamanho e linhas, limite de taxa por IP |
| CSV *injection* | Valores iniciados por `=`, `+`, `-`, `@` na exportação | Prefixar com apóstrofo ao gerar CSV no cliente |
| Zip bomb ou arquivo disfarçado | Upload fora do padrão | Validação de tipo, leitura limitada em *streaming* |
| Abuso de CORS | Origens não autorizadas | Lista de origens permitidas |
| Link malicioso vindo do arquivo | Profile URL com esquema javascript: ou domínio falso | O link é montado pelo servidor a partir do username validado; a URL do arquivo é ignorada |
| Contato involuntário com terceiros | Avatar URL aponta para CDN externo e faria o navegador do usuário contatar servidores do Instagram | Avatares nunca são carregados; a política de segurança do conteúdo limita imagens à própria origem |

### 12.2 LGPD

Os nomes de usuário listados são dados pessoais de terceiros. Como o sistema **não armazena, não compartilha e não registra** esses dados, o tratamento limita-se à execução da operação solicitada pelo próprio usuário, em memória e por tempo mínimo. Recomenda-se publicar uma política de privacidade clara, indicando finalidade, ausência de retenção e ausência de coleta de identificadores.

### 12.3 Termos da plataforma

O sistema não acessa o Instagram, não usa credenciais e não faz *scraping*. Trabalha apenas com arquivos que o usuário obteve legitimamente pela exportação oficial.

---

## 13. Riscos e Pontos em Aberto

| # | Risco | Impacto | Mitigação |
| --- | --- | --- | --- |
| 1 | Os CSVs não vêm do Instagram em formato padronizado e o formato pode mudar | Alto | Contrato de colunas flexível, com aliases, e conversor local no roadmap |
| 2 | Contas renomeadas geram falso positivo quando o arquivo não tem User Id | Médio | Usar o User Id como chave; sem ele, aviso na interface&#32; |
| 3 | Contas desativadas ou bloqueadas aparecem como unfollowers | Médio | Aviso ao usuário sobre a limitação dos dados |
| 4 | Arquivos temporários do servidor ASGI em uploads grandes | Médio | Validar tamanho em *streaming* e confirmar ausência de arquivos residuais |
| 5 | Consumo de memória do Pandas em picos de concorrência | Médio | Limites rígidos, fila de requisições e dimensionamento de instâncias |

---

## 14. Glossário

| Termo | Definição |
| --- | --- |
| *Snapshot* | Cópia da lista de conexões em um instante do tempo |
| Unfollower | Conta que estava na lista de seguidores no snapshot anterior e não está no atual |
| Mútuo | Conta que o usuário segue e que também o segue |
| Stateless | Sem estado persistente entre requisições |
| Normalização | Padronização dos identificadores antes da comparação |
| DataFrame | Estrutura tabular em memória da biblioteca Pandas |
| ASGI | Interface padrão entre servidores e aplicações assíncronas em Python |
| OpenAPI | Especificação padrão para descrever APIs REST |
| ADR | *Architecture Decision Record*, registro de decisão arquitetural |
| LGPD | Lei Geral de Proteção de Dados (Lei 13.709/2018) |
| User Id | Identificador numérico e estável de um perfil, presente no CSV de exemplo; não muda com a troca de username |
| Análise cruzada | Comparação entre a lista de seguidores e a de contas seguidas, ambas atuais |
| Redução do CSV | Remoção, no navegador, das colunas desnecessárias antes do envio ao servidor |
| Renomeado | Perfil com o mesmo User Id e Username diferente entre dois snapshots |

---

## 15. Roadmap

| Fase | Entregas |
| --- | --- |
| v1.0 | Comparação de snapshots em CSV, interface completa, contrato de API, testes e CI |
| v1.1 | Parser do JSON exportado pelo Instagram, com *adapter* de entrada |
| v1.2 | Processamento do arquivo no navegador via WebAssembly, eliminando o envio ao servidor |
| v2.0 | Comparação de mais de dois snapshots (linha do tempo local, com histórico mantido apenas no navegador) |

---

## 16. Especificação da Interface

A interface é uma página única, sem login e sem navegação entre telas. Todo o fluxo acontece na mesma página, em quatro blocos: aviso de privacidade, envio, resumo e resultados.

### 16.1 Estrutura da página (wireframe)

```text
Instagram Tracker
Seus arquivos são processados na hora e não são salvos.
Nenhuma conexão com o Instagram é feita.
──────────────────────────────────────────────────────────────
SEGUIDORES                          SEGUINDO
  Anterior [ Escolher ou arrastar ]   Anterior [ Escolher ou arrastar ]
  Atual    [ Escolher ou arrastar ]   Atual    [ Escolher ou arrastar ]
──────────────────────────────────────────────────────────────
Análises que serão geradas:  Seguidores · Seguindo · Cruzada
                  [ Comparar ]   [ Nova análise ]
──────────────────────────────────────────────────────────────
[Seguidores] [Seguindo] [Cruzada]
RESUMO   Deixaram de seguir: 12   Novos: 5   Mantidos: 1238
[Deixaram de seguir] [Novos] [Mantidos] [Renomeados]
Buscar: [____________]                    [ Exportar CSV ]
  • ana.costa  (Ana Costa)  [privada]            abrir perfil ↗
  • pedro.h                                      abrir perfil ↗
```

Na aba Seguindo, os grupos são *Deixei de seguir*, *Passei a seguir*, *Mantidos* e *Renomeados*. Na aba Cruzada, *Mútuos*, *Não seguem de volta* e *Fãs*. Só aparecem as abas das análises executadas.

### 16.2 Componentes

| Componente | Função | Requisitos |
| --- | --- | --- |
| Aviso de privacidade | Informa retenção zero e ausência de integração com o Instagram | RNF01, RNF19 |
| Campos de arquivo (×4) | Dois grupos, Seguidores e Seguindo, cada um com Anterior e Atual; seleção por clique ou *drag and drop*, com nome e tamanho | RF01, RNF18 |
| Indicador de análises | Mostra, em tempo real, quais análises os arquivos escolhidos formam e avisa quando um arquivo não participa de nenhuma | RF02 |
| Redução do CSV | Lê o arquivo no navegador, mantém `User Id`, `Username` e `Fullname` e monta o arquivo a enviar | RF17 |
| Botão "Comparar" | Habilitado quando há ao menos uma análise possível; envia a requisição | RF10 |
| Botão "Nova análise" | Limpa arquivos, resultados e mensagens | RF14 |
| Abas de análise e de grupo | Primeiro nível: Seguidores, Seguindo e Cruzada (só as executadas); segundo nível: os grupos de cada análise | RF11, RN07 |
| Painel de resumo | Contagens dos grupos da análise ativa | RF09 |
| Campo de busca | Filtra a lista ativa em tempo real, no cliente | RF11 |
| Lista de perfis | Mostra username, nome e selos de conta privada e verificada, sem imagem de avatar; o link `https://www.instagram.com/{username}` abre em nova aba com `rel="noopener noreferrer"` | RF11, RF18 |
| Botão "Exportar CSV" | Gera o arquivo localmente com `Blob` | RF12 |
| Região de mensagens | Erros e avisos, com `aria-live="polite"` | RF13, RNF16 |

O link para o perfil é apenas uma navegação feita pelo próprio usuário: o sistema não consulta o Instagram para montá-lo.

### 16.3 Estados da interface

| Estado | Condição | O que o usuário vê |
| --- | --- | --- |
| Inicial | Nenhum arquivo escolhido | Campos vazios, "Comparar" desabilitado |
| Pronto | Arquivos que formam ao menos uma análise | "Comparar" habilitado |
| Carregando | Requisição em andamento | Botão desabilitado, indicador de progresso, campos bloqueados |
| Sucesso | Resposta 200 | Resumo e abas visíveis, foco movido para o resumo |
| Sem mudanças | 200 com `houve_mudanca = false` | Aviso "Nenhuma mudança entre os dois arquivos" |
| Erro de validação | Resposta 400, 413 ou 422 | Mensagem do catálogo (seção 10.1) e destaque no campo envolvido |
| Erro de rede ou 5xx | Falha de conexão ou 500 | Mensagem genérica e botão "Tentar novamente", arquivos mantidos |

Transições: Inicial → Pronto → Carregando → (Sucesso, Sem mudanças ou Erro). De qualquer estado, "Nova análise" volta ao Inicial.

### 16.4 Validações no cliente

| Validação | Regra | Mensagem |
| --- | --- | --- |
| Extensão | Termina em `.csv` | "Escolha um arquivo .csv." |
| Tamanho original | Até 100 MB, lidos em blocos pelo navegador | "Este arquivo é grande demais para ser lido." |
| Coluna | O cabeçalho tem `Username` | "Não encontramos a coluna Username neste arquivo." |
| Tamanho após a redução | Até 25 MB | "O arquivo reduzido passa de 25 MB." |
| Combinação | Ao menos uma análise possível | "Escolha dois arquivos de seguidores, dois de seguindo, ou um de cada." |

A validação no cliente é só conveniência. A validação definitiva é sempre a do servidor.

### 16.5 Acessibilidade e responsividade

| Item | Especificação |
| --- | --- |
| Teclado | Todos os controles alcançáveis por `Tab`; abas navegáveis com setas |
| Rótulos | Cada campo de arquivo com `<label>` associado |
| Foco | Indicador de foco visível; foco movido ao resumo após o sucesso |
| Contraste | Mínimo 4,5:1 para texto comum |
| Leitores de tela | Erros e estados de carregamento anunciados via `aria-live` |
| Mobile | Layout em coluna única a partir de 360 px; alvos de toque de pelo menos 44 px |
| Tema | Respeita `prefers-color-scheme` (claro e escuro) |
| Listas longas | Renderização em lotes (ex.: 200 itens por vez) para manter a fluidez com dezenas de milhares de nomes |

---

## 17. Obtenção dos Arquivos pelo Usuário

Como o sistema não acessa o Instagram, **o usuário é a única fonte de dados**. Esta seção descreve o caminho de ponta a ponta, do pedido de exportação até o CSV aceito pelo sistema.

### 17.1 Fluxo de obtenção

1. O usuário solicita ao Instagram, pelos recursos oficiais da própria plataforma, uma cópia de suas informações, incluindo seguidores e contas seguidas.
2. O Instagram prepara o pacote e o disponibiliza para download ao usuário, que o baixa por conta própria.
3. O usuário extrai do pacote os arquivos de seguidores e de contas seguidas.
4. O usuário converte cada arquivo para o formato de CSV aceito (seção 9.1), se ainda não estiver nele.
5. Algum tempo depois, repete o processo para obter um segundo snapshot.
6. O usuário envia os dois snapshots ao Instagram Tracker.

O caminho exato dos menus e os nomes dos arquivos do pacote são definidos pelo Instagram e podem mudar. A documentação deve ser conferida contra a versão atual do aplicativo antes de cada release.

O formato do arquivo de exemplo (colunas `User Id`, `Username`, `Avatar URL` e outras) é produzido fora do sistema, por uma ferramenta que o usuário escolhe por conta própria. O Instagram Tracker não depende dessa ferramenta, não a chama e não a controla: ele apenas lê o CSV que o usuário selecionar.

### 17.2 Boas práticas para o usuário

| Prática | Motivo |
| --- | --- |
| Guardar cada exportação com a data no nome (ex.: `seguidores_2026-10-07.csv`) | O sistema não guarda histórico; o usuário precisa dos snapshots antigos |
| Manter intervalos regulares entre exportações | Facilita interpretar o que mudou e quando |
| Usar sempre o mesmo formato de exportação | Evita divergências na conversão |
| Não compartilhar os arquivos exportados | Contêm dados de terceiros |

### 17.3 Conversão para o CSV canônico

O sistema aceita diretamente CSVs no formato da seção 9.1, como o arquivo de exemplo do projeto. Quem partir do pacote JSON ou HTML do Instagram precisa convertê-lo antes. Enquanto o sistema não incorpora um conversor próprio, há duas opções, ambas sem enviar dados a terceiros:

| Opção | Descrição | Autonomia |
| --- | --- | --- |
| Conversão manual | Abrir o arquivo e copiar os usernames para uma planilha com a coluna `username`, exportando como CSV | Total |
| Conversor local (previsto na v1.1) | Script em `tools/` ou módulo JavaScript que lê o JSON no navegador e gera o CSV canônico, sem rede | Total |

O conversor local é uma etapa de **pré-processamento**, separada do núcleo de comparação. Ele não altera as regras de negócio, e a API continua aceitando apenas o CSV canônico.

### 17.4 Limitações inerentes à entrada manual

| Limitação | Efeito sobre o resultado |
| --- | --- |
| Exportação desatualizada | O resultado reflete o momento da exportação, não o presente |
| Dois snapshots muito distantes no tempo | Várias mudanças ocorridas no intervalo aparecem juntas |
| Troca de nome de usuário entre snapshots | Com User Id, a conta é reconhecida como renomeada; sem ele, aparece como unfollower e como novo seguidor |
| Conta desativada, suspensa ou que bloqueou o usuário | Aparece como unfollower, sem indicação do motivo |

---

## 18. Plano de Implementação

O desenvolvimento segue uma ordem de dentro para fora: primeiro o núcleo puro de comparação, depois a API, depois a interface. Cada fase só termina quando seu critério de saída é atendido.

### 18.1 Fases

| Fase | Entregáveis | Critério de saída | Esforço relativo |
| --- | --- | --- | --- |
| 0. Fundações | Repositório, `pyproject.toml`, estrutura de pastas, lint, tipagem e CI vazio funcionando | CI verde em um commit inicial | Pequeno |
| 1. Núcleo | `normalizacao.py`, `comparador.py` e testes unitários e de propriedade (CT01 a CT05, CT22 e CT23) | Invariantes da seção 6.3 verdadeiras em 1.000 casos aleatórios | Médio |
| 2. Leitura de CSV | `leitor_csv.py` com detecção de separador, BOM, aliases e erros de domínio | CT06, CT07 e erros 400/422 cobertos | Médio |
| 3. API | Rotas `/comparar` e `/saude`, schemas Pydantic, handlers de erro, limite de taxa, cabeçalhos de segurança | CT08 a CT13, CT20 e CT21 passando; OpenAPI gerado confere com o contrato | Médio |
| 4. Interface | `index.html`, estilos, `api.js`, `ui.js`, `exportar.js`, redução do CSV no navegador (reduzir.js), estados da seção 16.3 | Fluxo completo UC01 a UC08 e CT25 em Chrome, Firefox, Safari e Edge | Grande |
| 5. Endurecimento | Testes de privacidade, autonomia, segurança e desempenho (CT14 a CT19 e CT24 a CT26) | Metas RNF10 a RNF12 atingidas; auditoria WCAG sem falhas críticas | Médio |
| 6. Empacotamento | Dockerfile, README, política de privacidade, guia do usuário (seção 17) | Execução local e via Docker descritas e verificadas do zero | Pequeno |

### 18.2 Definição de pronto (DoD)

Uma entrega é considerada pronta quando:

- Todos os critérios de aceite relacionados (seção 5.4) passam.
- O código passa em `ruff` e `mypy` sem avisos.
- A cobertura do núcleo de serviços é de pelo menos 85%.
- Nenhum teste de privacidade ou autonomia (CT14 a CT16) falha.
- A documentação afetada está atualizada.
- Um revisor aprovou o *pull request*.

### 18.3 Dependências entre fases

Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 5 → Fase 6. A Fase 4 (interface) pode começar assim que o contrato OpenAPI da Fase 3 estiver congelado, usando respostas simuladas, e termina antes da Fase 5.

### 18.4 Riscos do plano

| Risco | Mitigação |
| --- | --- |
| Pandas excede o limite de memória em arquivos grandes | Ler apenas a coluna necessária (`usecols`) e medir cedo, na Fase 2 |
| Divergência entre contrato e implementação | Gerar o OpenAPI a partir do código e comparar com `docs/openapi.yaml` no CI |
| Formato de exportação do Instagram mudar | Manter o CSV canônico como contrato estável e isolar a conversão em módulo separado |
| Dados reais vazarem para o repositório | Usar apenas fixtures sintéticas e bloquear arquivos `.csv` fora de `tests/fixtures/` com *hook* de pré-commit |

---

## 19. Métricas de Sucesso e Perguntas Frequentes

### 19.1 Métricas de sucesso

Por respeito à privacidade e à autonomia (RNF01, RNF19), o sistema **não coleta telemetria de uso nem usa serviços de análise**. As métricas abaixo são todas técnicas e verificadas em testes, não por rastreamento de usuários.

| Métrica | Meta | Como medir |
| --- | --- | --- |
| Correção da classificação | 100% dos casos de teste e invariantes | Suíte `pytest` e `hypothesis` |
| Tempo de resposta (100 mil linhas) | p95 ≤ 2 s | Teste de carga |
| Tempo de resposta (500 mil linhas) | p95 ≤ 8 s | Teste de carga |
| Memória por requisição | ≤ 512 MB | Medição durante o teste de carga |
| Retenção de dados | Zero arquivos e zero registros com dados de usuário | CT14 |
| Dependência externa | Zero chamadas de rede de saída | CT15 e CT16 |
| Cobertura de testes (núcleo) | ≥ 85% | `pytest-cov` |
| Acessibilidade | Sem falhas críticas WCAG 2.1 AA | Auditoria Lighthouse e verificação manual |
| Compatibilidade | Fluxo completo nos 4 navegadores-alvo | Teste manual por release |

### 19.2 Perguntas frequentes

| Pergunta | Resposta |
| --- | --- |
| Preciso informar minha senha do Instagram? | Não. O sistema nunca pede senha, token ou qualquer credencial, e nem se conecta ao Instagram |
| O sistema acessa minha conta? | Não. Ele só lê os arquivos que você escolhe enviar |
| Meus arquivos ficam guardados? | Não. São processados em memória e descartados ao final da requisição |
| Funciona sem internet? | Sim, no modo local (seção 7.5), pois o sistema não depende de serviços externos |
| Por que o sistema não mostra o histórico de meses anteriores? | Porque não guarda nada. Para comparar, você reenvia os dois snapshots que quiser |
| Por que alguém aparece como unfollower se apenas mudou de nome? | Com a coluna User Id, o sistema reconhece a mesma conta e a lista como renomeada. Sem ela, a troca faz a conta parecer duas pessoas diferentes |
| O sistema avisa o motivo de alguém ter deixado de seguir? | Não. Os arquivos não trazem essa informação |
| Posso usar na conta de um cliente? | Apenas com autorização do titular, pois os arquivos contêm dados pessoais de terceiros |
| O sistema deixa de seguir ou bloqueia contas por mim? | Não. Ele só analisa e exibe listas; nenhuma ação é feita no Instagram |
| Preciso enviar os quatro arquivos? | Não. Dois de seguidores mostram quem saiu e quem entrou; dois de seguindo mostram quem você deixou de seguir ou passou a seguir; um de cada, ambos atuais, mostra quem você segue e não segue de volta |
| Por que o navegador mexe no meu arquivo antes de enviar? | Ele só descarta colunas que o sistema não usa, como a URL do avatar. Isso reduz o arquivo em mais de 90% e evita enviar dados desnecessários |

---

## 20. Referências

- Especificação OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.3
- Documentação do FastAPI: https://fastapi.tiangolo.com
- Documentação do Pandas (`read_csv`): https://pandas.pydata.org/docs
- WCAG 2.1: https://www.w3.org/TR/WCAG21/
- OWASP Top 10 e CSV Injection: https://owasp.org
- Lei Geral de Proteção de Dados (Lei 13.709/2018): https://www.planalto.gov.br/ccivil\_03/\_ato2015-2018/2018/lei/l13709.htm
