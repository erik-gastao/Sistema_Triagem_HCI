# Manual de Instalação - Sistema de Triagem HCI

Este manual detalha o processo de instalação e configuração do Sistema de Triagem HCI com as melhorias implementadas.

## Requisitos do Sistema

### Frontend
- Node.js 20.9 ou superior
- NPM 10.x ou superior
- Navegador moderno (Chrome, Firefox, Edge, Safari)

### Backend
- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)
- SQLite 3
- Ollama instalado localmente com o modelo configurado em `OLLAMA_MODEL` (padrão `llama3.2:3b`)

## Estrutura do Projeto

O sistema está dividido em duas partes principais:

```
Sistema_Triagem_HCI/
├── frontend/         # Aplicação Next.js para interface do usuário
├── backend/          # API FastAPI para processamento de triagem e usuários
└── .env.example      # Modelo de configuração do backend
```

## 1. Instalação do Backend

1. Navegue até a pasta do backend:
   ```bash
   cd Sistema_Triagem_HCI/backend
   ```

2. Crie e ative um ambiente virtual Python:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências (torch sem CUDA é bem menor; use o índice padrão se tiver GPU NVIDIA):
   ```bash
   pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
   pip install -r requirements.txt
   ```

4. Verifique se o Ollama está instalado e o modelo está disponível:
   ```bash
   # Instalar Ollama (se necessário)
   curl -fsSL https://ollama.com/install.sh | sh

   # Baixar o modelo usado na triagem
   ollama pull llama3.2:3b

   # Iniciar o serviço Ollama
   ollama serve
   ```

5. Inicie o servidor backend:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 2. Instalação do Frontend

1. Navegue até a pasta do frontend:
   ```bash
   cd Sistema_Triagem_HCI/frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

4. Para build de produção:
   ```bash
   npm run build
   npm start
   ```

## 3. Configuração do Sistema

### Configuração do Backend

O backend utiliza um arquivo `.env` para configurações. Copie `.env.example` (na raiz
do projeto) para `backend/.env` e ajuste conforme necessário:

```
# ---------- Ollama ----------
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# ---------- Backend ----------
CORS_ORIGINS=http://localhost:3000
N_CASOS_SIMILARES=3
EMBEDDING_MODEL=pucpr/biobertpt-clin

# Caminhos de dados (relativos a backend/)
DB_PATH=./validacao_triagem.db
CHROMA_PATH=./chroma_db
EMBEDDING_CACHE_DIR=./embedding_cache
```

### Configuração do Frontend

O frontend utiliza um arquivo `.env.local` para configurações. Crie um arquivo `.env.local` na pasta `frontend` com o seguinte conteúdo:

```
# URL da API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Configurações da aplicação
NEXT_PUBLIC_APP_NAME=Sistema de Triagem HCI
```

## 4. Verificação da Instalação

1. Acesse o frontend em: http://localhost:3000
2. Acesse a documentação da API em: http://localhost:8000/docs
3. Verifique o status dos serviços em: http://localhost:8000/api/status

## 5. Usuários Padrão

O sistema cria automaticamente os seguintes usuários para demonstração:

| Usuário    | Senha     | Função       |
|------------|-----------|--------------|
| admin      | admin     | Administrador|
| medico     | medico    | Médico       |
| enfermeiro | enfermeiro| Enfermeiro   |

## 6. Solução de Problemas

### Problemas com o Ollama

Se o sistema não conseguir se comunicar com o Ollama, verifique:

1. Se o serviço Ollama está em execução:
   ```bash
   # Linux/Mac
   ps aux | grep ollama

   # Windows (PowerShell)
   Get-Process ollama -ErrorAction SilentlyContinue
   ```

2. Se o modelo configurado em `OLLAMA_MODEL` está disponível:
   ```bash
   ollama list
   ```

3. Se a porta 11434 está acessível:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Problemas com o Backend

1. Verifique os logs em `triagem_api.log`, `embedding_service.log` e `ollama_service.log`
2. Certifique-se de que todas as dependências foram instaladas corretamente
3. Verifique se o banco de dados SQLite foi criado corretamente

### Problemas com o Frontend

1. Limpe o cache do Node:
   ```bash
   npm cache clean --force
   ```

2. Remova a pasta `node_modules` e reinstale as dependências:
   ```bash
   rm -rf node_modules
   npm install
   ```

3. Verifique se a URL da API está configurada corretamente no arquivo `.env.local`
