# Sistema de Triagem - Backend FastAPI

Backend do Sistema de Triagem HCI, baseado no Protocolo de Manchester, com FastAPI e integração com Ollama.

## Requisitos

- Python 3.10 ou superior
- Ollama instalado e rodando
- Modelo configurado em `OLLAMA_MODEL` baixado no Ollama (padrão: `llama3.2:3b`)
- Dependências listadas em `requirements.txt`

## Pré-requisitos do Ollama

1. Instale o Ollama: https://ollama.com/download

2. Baixe o modelo usado na triagem:
```bash
ollama pull llama3.2:3b
```

Em máquinas sem GPU NVIDIA, `llama3.2:3b` responde em ~8-15s por triagem (~2GB RAM).
`mistral` (7B) dá respostas melhores, mas leva ~20-40s e exige ~4.5GB de RAM.

3. Inicie o servidor Ollama:
```bash
ollama serve
```

## Instalação

1. Crie um ambiente virtual:
```bash
python -m venv venv
```

2. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instale as dependências (torch sem CUDA é bem menor; use o índice padrão se tiver GPU NVIDIA):
```bash
pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

4. Configure o `.env` (copie de `../.env.example`):
```bash
copy ..\.env.example .env    # Windows
# cp ../.env.example .env    # Linux/Mac
```

## Executando o servidor

1. Certifique-se de que o Ollama está rodando:
```bash
ollama serve
```

2. Execute o servidor FastAPI:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

O servidor estará disponível em `http://localhost:8000`. Na primeira execução, o modelo
de embeddings (`pucpr/biobertpt-clin`, ~500MB) é baixado do Hugging Face e cacheado localmente.

## Documentação da API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints principais

- `GET /`: Página inicial da API
- `GET /api/status`: Status dos serviços (Ollama, banco, ChromaDB)
- `POST /api/triagem`: Processa e salva triagem no banco para validação
- `GET /api/triagens`: Lista triagens (com filtro opcional de pendentes/todas)
- `POST /api/validar`: Valida ou ajusta a classificação de uma triagem
- `GET /api/estatisticas`: Estatísticas do sistema (totais, precisão)
- `POST /api/login`: Autentica usuário
- `POST /api/usuarios`: Cadastra usuário
- `GET /api/usuarios`: Lista usuários
- `GET /api/usuarios/{usuario_id}`: Detalha usuário
- `PUT /api/usuarios/{usuario_id}`: Atualiza usuário
- `DELETE /api/usuarios/{usuario_id}`: Remove usuário

## Estrutura do projeto

- `main.py`: Endpoints de triagem/validação, banco SQLite e busca vetorial
- `embedding_service.py`: Geração de embeddings clínicos (BioBERTpt) + cache
- `ollama_service.py`: Prompt de Manchester e chamada ao Ollama
- `usuarios.py`: Gestão de usuários (hash de senha, CRUD, autenticação)
- `rotas_usuarios.py`: Rotas de usuários e login (router `/api`)
- `requirements.txt`: Lista de dependências Python
- `validacao_triagem.db`: Banco de dados SQLite (criado automaticamente)
- `chroma_db/`: Banco de dados vetorial ChromaDB (criado automaticamente)

## Funcionalidades

- **Processamento com IA**: Modelo via Ollama (padrão `llama3.2:3b`) para classificação
- **Embeddings**: BioBERTpt em português para busca de casos similares (RAG)
- **Banco Vetorial**: ChromaDB para armazenar casos históricos
- **Validação**: Sistema de validação/ajuste de classificação por especialistas
- **Dashboard**: Interface administrativa para monitoramento (ver `frontend/`)

## Troubleshooting

1. **Erro "Ollama não encontrado"**: Certifique-se de que o Ollama está instalado e rodando (`ollama serve`)
2. **Erro de modelo**: Execute `ollama pull llama3.2:3b` (ou o modelo definido em `OLLAMA_MODEL`)
3. **Erro de dependências**: Execute `pip install -r requirements.txt`
