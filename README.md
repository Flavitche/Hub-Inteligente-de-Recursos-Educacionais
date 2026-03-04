# Hub Inteligente de Recursos Educacionais

Esse projeto é uma aplicação fullstack para cadastrar e organizar recursos educacionais como vídeos, PDFs e links. O diferencial é que ele tem uma integração com IA, você digita o título do recurso, clica num botão, e o sistema gera automaticamente uma descrição e as tags usando o modelo llama da Groq.

Foi construído com FastAPI no backend, React no frontend, SQLite como banco de dados (com suporte a PostgreSQL), e tem pipeline de CI/CD configurado no GitHub Actions.

---

## O que o sistema faz

- Cadastrar, editar, visualizar e excluir recursos educacionais
- Listar os recursos com paginação, filtro por tipo e busca por texto
- Gerar descrição e tags automaticamente via IA (Groq API)
- Logar cada chamada à IA com título, tokens usados e tempo de resposta
- Verificar se a aplicação está saudável via endpoint `/health`

---

## Tecnologias usadas

**Backend:**
- Python 3.11
- FastAPI — framework principal da API
- SQLAlchemy 2.0 — ORM para o banco de dados
- Pydantic v2 — validação dos dados
- httpx — cliente HTTP assíncrono para chamar a Groq
- tenacity — retry automático com backoff exponencial
- python-dotenv — leitura do arquivo `.env`

**Frontend:**
- React 18 com Vite
- Axios — chamadas HTTP para o backend
- CSS puro com variáveis — sem biblioteca de UI

**DevOps:**
- Docker e Docker Compose
- GitHub Actions — pipeline de CI/CD
- Black, Flake8, isort — formatação e linting
- Bandit — verificação de segurança no código

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 18 ou superior
- Uma chave de API da Groq (gratuita em https://console.groq.com)

### Backend

```bash
# Entre na pasta do backend
cd hub_educacional

# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac e Linux

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo .env manualmente na pasta hub_educacional/
# Cole o conteúdo abaixo e preencha com seus valores:

DATABASE_URL=sqlite:///./hub_educacional.db
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=512
GROQ_TEMPERATURE=0.4
ENVIRONMENT=development
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:5173"]

# Suba o servidor
uvicorn app.main:app --reload --port 8000
```

O servidor vai subir em http://localhost:8000

A documentação interativa fica em http://localhost:8000/docs, lá você consegue testar todos os endpoints sem precisar de nenhuma ferramenta extra.

### Frontend

Abre um segundo terminal e rode:

```bash
# Entre na pasta do frontend
cd frontend

# Instale as dependências (só precisa fazer isso uma vez)
npm install

# Suba o servidor de desenvolvimento
npm run dev
```

O frontend vai abrir em http://localhost:5173

---

## Como rodar com Docker

Se quiser rodar tudo junto com PostgreSQL em vez de SQLite:

```bash
# Entre na pasta do backend
cd hub_educacional

# Suba tudo
docker-compose up --build
```

Isso vai subir dois containers:
- O backend FastAPI na porta 8000
- O PostgreSQL na porta 5432

Para parar tudo:

```bash
docker-compose down
```

Para ver os logs em tempo real:

```bash
docker-compose logs -f backend
```


---

## Populando o banco com dados de exemplo (seed)

O banco de dados não vai para o GitHub, então quem clonar o projeto começa com o banco vazio. Se quiser ter alguns recursos de exemplo logo de cara, rode o script de seed:

```bash
cd hub_educacional
python seed.py
```

A saída vai ser assim:

```
🌱 Iniciando seed do banco de dados...

   ✅ Video  — Python para Iniciantes — Curso Completo
   ✅ PDF    — Estruturas de Dados e Algoritmos em Python
   ✅ Link   — Documentação Oficial do FastAPI
   ✅ Video  — SQL para Análise de Dados — Do Zero ao Avançado
   ✅ PDF    — React — Guia Completo com Hooks e Context API
   ✅ Video  — Docker — Containerização para Desenvolvedores

🎉 Seed concluído! 6 recursos criados com sucesso.
```

Dois detalhes importantes:

**Proteção contra duplicatas** — se o banco já tiver dados, o script avisa e não insere nada. Pode rodar quantas vezes quiser sem duplicar.

**Recriar do zero** — se quiser limpar tudo e começar de novo, delete o arquivo `hub_educacional.db` e rode o seed novamente:

```bash
# Windows
del hub_educacional.db

# Mac e Linux
rm hub_educacional.db

# Depois rode o seed novamente
python seed.py
```

Depois do seed, suba o servidor normalmente e os recursos já vão aparecer no frontend. A partir daí a aplicação funciona normalmente — você cria, edita e exclui os recursos que quiser. O banco é local, então o que cada pessoa cadastrar fica só na máquina dela.

---

## Variáveis de ambiente

O arquivo `.env` fica na pasta `hub_educacional/`. Nunca sobe para o GitHub, está no `.gitignore`.

| Variável | O que é | Valor padrão |
|----------|---------|--------------|
| `DATABASE_URL` | Conexão com o banco | `sqlite:///./hub_educacional.db` |
| `GROQ_API_KEY` | Chave da API Groq — obrigatória | — |
| `GROQ_MODEL` | Modelo de IA usado | `llama-3.3-70b-versatile` |
| `GROQ_MAX_TOKENS` | Limite de tokens na resposta | `512` |
| `GROQ_TEMPERATURE` | Criatividade da IA, de 0 a 1 | `0.4` |
| `ENVIRONMENT` | Ambiente de execução | `development` |
| `LOG_LEVEL` | Nível dos logs | `INFO` |
| `ALLOWED_ORIGINS` | Origens permitidas no CORS | `["http://localhost:5173"]` |

---

## Estrutura do projeto

```
Hub-Inteligente-de-Recursos-Educacionais/
│
├── hub_educacional/              — backend
│   ├── app/
│   │   ├── main.py               — cria o FastAPI, registra routers e middlewares
│   │   ├── api/
│   │   │   └── routers/
│   │   │       ├── resources.py  — endpoints do CRUD
│   │   │       ├── ai.py         — endpoint POST /ai/generate
│   │   │       └── health.py     — endpoint GET /health
│   │   ├── core/
│   │   │   ├── config.py         — lê o .env e valida as configurações
│   │   │   ├── logging.py        — configura os logs (JSON em prod, colorido em dev)
│   │   │   ├── exceptions.py     — exceções de domínio da aplicação
│   │   │   └── security.py       — proteção e validação da API key
│   │   ├── db/
│   │   │   └── session.py        — engine, sessão e conexão com o banco
│   │   ├── models/
│   │   │   └── resource.py       — tabela do banco via SQLAlchemy
│   │   ├── schemas/
│   │   │   ├── resource.py       — schemas Pydantic: Create, Update, Response
│   │   │   └── ai.py             — schemas do endpoint de IA
│   │   └── services/
│   │       ├── resource_service.py — toda a lógica do CRUD
│   │       └── ai_service.py       — integração com a Groq
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│
├── frontend/                     — frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx        — cabeçalho com navegação
│   │   │   ├── ResourceCard.jsx  — card individual de cada recurso
│   │   │   ├── Pagination.jsx    — navegação entre páginas
│   │   │   └── Toast.jsx         — notificações de sucesso e erro
│   │   ├── pages/
│   │   │   ├── ResourceList.jsx  — tela de listagem com filtros
│   │   │   └── ResourceForm.jsx  — formulário de cadastro e edição
│   │   ├── hooks/
│   │   │   └── useResources.js   — lógica de estado separada dos componentes
│   │   ├── services/
│   │   │   └── api.js            — configuração do Axios
│   │   ├── App.jsx               — componente raiz, controla qual tela exibir
│   │   └── main.jsx              — ponto de entrada do React
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
└── .github/
    └── workflows/
        └── ci.yml                — pipeline que roda a cada push
```

---

## Endpoints da API

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/health` | Verifica se a API e o banco estão funcionando |
| POST | `/resources/` | Cria um novo recurso |
| GET | `/resources/` | Lista recursos com paginação e filtros |
| GET | `/resources/{id}` | Busca um recurso pelo ID |
| PATCH | `/resources/{id}` | Atualiza parcialmente um recurso |
| DELETE | `/resources/{id}` | Remove um recurso |
| POST | `/ai/generate` | Gera descrição e tags via IA |

### Exemplo de listagem com filtros

```
GET /resources/?page=1&page_size=10&type=Video&search=python
```

### Exemplo de criação

```bash
curl -X POST http://localhost:8000/resources/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python para Iniciantes",
    "description": "Curso introdutório de Python",
    "type": "Video",
    "url": "https://youtube.com/watch?v=exemplo",
    "tags": ["python", "iniciante"]
  }'
```

---

## Endpoint de IA

```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Matemática Financeira para Concursos",
    "type": "PDF"
  }'
```

Resposta:

```json
{
  "description": "Você quer passar no concurso e a Matemática Financeira está no caminho? Este material foi feito pra isso. Aqui você vai aprender juros simples e compostos, séries de pagamentos, amortização e análise de investimentos — tudo com exercícios resolvidos e fórmulas comentadas. O conteúdo é voltado para nível intermediário e foi estruturado para quem precisa de clareza e velocidade na hora da prova. Com dedicação, você vai sair daqui pronto para resolver qualquer questão financeira com confiança.",
  "tags": ["matemática financeira", "concurso", "juros compostos", "amortização", "intermediário"]
}
```

Log gerado no terminal:

```
[INFO] AI Request: Title="Matemática Financeira para Concursos", TokenUsage=312, Latency=1.8s
```

---

## Pipeline de CI/CD

A cada `git push`, o GitHub Actions roda automaticamente:

1. Instala as dependências
2. Roda o **Black** — verifica se o código está formatado corretamente
3. Roda o **isort** — verifica se os imports estão organizados
4. Roda o **Flake8** — verifica erros de estilo e boas práticas
5. Roda o **Bandit** — verifica vulnerabilidades de segurança no código
6. Roda os **testes** com pytest

Se qualquer etapa falhar, o push fica marcado com ❌ no GitHub e você sabe exatamente o que corrigir.

---

## Decisões que tomei no projeto

**Por que arquitetura em camadas?**
Porque cada parte do código tem uma responsabilidade clara. O router só lida com HTTP. O service só lida com a lógica. O model só define o banco. Se precisar trocar o banco de SQLite para PostgreSQL, só muda a camada de banco — o resto não precisa saber disso.

**Por que PATCH em vez de PUT na atualização?**
PUT substituiria o recurso inteiro — se você não mandasse todos os campos, eles seriam zerados. PATCH atualiza só o que você manda. Isso é feito com `model_dump(exclude_unset=True)` no Pydantic, que retorna só os campos que foram enviados na requisição.

**Por que httpx em vez de requests?**
O `requests` é síncrono — bloqueia o servidor inteiro enquanto espera a resposta da Groq. O `httpx` é assíncrono — o servidor continua atendendo outras requisições enquanto espera. Isso importa muito num endpoint que pode demorar 2 a 3 segundos.

**Por que tenacity para retry?**
Porque APIs externas falham. A Groq pode retornar 429 (muitas requisições) ou 503 (sobrecarga). Em vez de simplesmente falhar e dar erro para o usuário, o sistema tenta 3 vezes automaticamente com espera crescente entre as tentativas — 1 segundo, depois 2, depois 4.

**Por que dataclasses com `frozen=True`?**
Quando a Groq responde, agrupamos os dados em uma dataclass imutável. `frozen=True` garante que ninguém vai alterar esses dados acidentalmente depois que foram criados. É uma proteção extra contra bugs difíceis de rastrear.

**Por que JSONList customizado para tags?**
O SQLite não tem tipo ARRAY nativo. Criamos um tipo customizado que salva a lista como string JSON no banco e converte de volta para lista Python automaticamente quando lê. Funciona tanto com SQLite quanto com PostgreSQL sem mudar nada no código.

**Por que Dockerfile multi-stage?**
O stage `builder` instala todas as ferramentas de compilação necessárias. O stage `runtime` copia só os pacotes já instalados, sem as ferramentas. A imagem final fica menor e mais segura — sem gcc, sem pip, sem nada que não seja necessário para rodar.
