# Sistema de Triagem HCI

<div align="center">
  <img src="https://hci.org.br/wp-content/uploads/2024/09/logo-300x67.png" alt="Logo HCI" width="300"/>
  <h3>Sistema Inteligente de Triagem Clínica</h3>
  <p>Baseado no Protocolo de Manchester com Inteligência Artificial</p>
</div>

## 📋 Sobre o Projeto

O Sistema de Triagem HCI é uma aplicação completa para triagem clínica hospitalar, desenvolvida especificamente para o Hospital de Clínicas de Ijuí (HCI). O sistema utiliza inteligência artificial através do modelo Mistral via Ollama para classificar pacientes de acordo com o Protocolo de Manchester, priorizando o atendimento conforme a gravidade dos casos.

### Principais Funcionalidades

- **Triagem Inteligente**: Classificação automática de pacientes baseada em sintomas
- **Validação Clínica**: Interface para validação das triagens por profissionais de saúde
- **Gestão de Usuários**: Sistema completo de cadastro e gerenciamento de usuários
- **Dashboard Administrativo**: Visualização de estatísticas e métricas de desempenho
- **Aprendizado Contínuo**: Melhoria progressiva da precisão através de feedback

## 🚀 Tecnologias

### Frontend
- **Next.js**: Framework React para renderização de páginas
- **CSS Moderno**: Design responsivo e adaptável a qualquer dispositivo
- **Componentes Reutilizáveis**: Arquitetura modular e escalável

### Backend
- **FastAPI**: Framework Python de alta performance
- **SQLite**: Banco de dados relacional para armazenamento de dados
- **ChromaDB**: Banco de dados vetorial para busca semântica
- **Ollama/Mistral**: Modelo de linguagem para processamento de triagem

## 🔧 Instalação

### Pré-requisitos
- Node.js 20.9 ou superior
- Python 3.10 ou superior
- [Ollama](https://ollama.com/download) instalado e em execução

### 1. Ollama

```bash
# Baixar o modelo usado na triagem
ollama pull llama3.2:3b

# Conferir que o servidor responde
curl http://localhost:11434/api/tags
```

Em máquinas sem GPU NVIDIA, um modelo 3B responde em ~8-15s por triagem.
`mistral` (7B) dá respostas melhores, mas leva ~20-40s e exige ~4.5 GB de RAM.
O modelo é configurável por `OLLAMA_MODEL` — veja `.env.example`.

### 2. Backend

```bash
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# torch sem CUDA (bem menor; use o índice padrão se tiver GPU NVIDIA)
pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu

# Demais dependências
pip install -r requirements.txt

# Configuração
copy ..\.env.example .env    # Windows
# cp ../.env.example .env    # Linux/Mac

# Iniciar servidor
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Na primeira execução o modelo de embeddings (`pucpr/biobertpt-clin`, ~500 MB)
é baixado do Hugging Face. Depois fica em cache local.

### 3. Frontend

```bash
cd frontend

npm install
npm run dev          # desenvolvimento em http://localhost:3000

# Produção
npm run build
npm start
```

A URL da API fica em `frontend/.env.local` (`NEXT_PUBLIC_API_URL`). Como é uma
variável `NEXT_PUBLIC_*`, ela é embutida no bundle em tempo de build — alterá-la
exige rodar `npm run build` de novo.

## 🖥️ Uso do Sistema

### Triagem de Pacientes

1. Acesse a página inicial
2. Preencha o formulário com os sintomas do paciente
3. Clique em "Realizar Triagem"
4. Visualize a classificação, justificativa e condutas recomendadas

### Área Administrativa

1. Acesse a área administrativa através do botão no canto superior direito
2. Faça login com suas credenciais
3. Navegue pelo dashboard para visualizar estatísticas
4. Gerencie usuários e valide triagens pendentes

Para instruções detalhadas, consulte o [Guia de Uso para Administradores](Guia%20de%20Uso%20para%20Administradores%20-%20Sistema%20de%20Triagem%20HCI.md).

## 📚 Documentação Adicional

- [Manual de Instalação](Manual%20de%20Instalação%20-%20Sistema%20de%20Triagem%20HCI.md)
- [Guia de Uso para Administradores](Guia%20de%20Uso%20para%20Administradores%20-%20Sistema%20de%20Triagem%20HCI.md)
- [Guia de Desenvolvimento](GUIA_DESENVOLVIMENTO.md)
- [README do Backend](backend/README.md)

## 🔍 Estrutura do Projeto

```
Sistema_Triagem_HCI/
├── backend/                  # API e lógica de negócio
│   ├── main.py               # Endpoints, banco SQLite e busca vetorial
│   ├── embedding_service.py  # Embeddings clínicos (BioBERTpt) + cache
│   ├── ollama_service.py     # Prompt de Manchester e chamada ao Ollama
│   ├── usuarios.py           # Gestão de usuários
│   ├── rotas_usuarios.py     # Rotas de usuários e login
│   └── requirements.txt      # Dependências Python
│
├── frontend/                 # Interface de usuário
│   ├── components/           # Componentes reutilizáveis
│   ├── lib/api.js            # Cliente HTTP central (baseURL da API)
│   ├── pages/                # Páginas da aplicação
│   ├── styles/               # Estilos CSS
│   └── package.json          # Dependências JavaScript
│
└── .env.example              # Modelo de configuração do backend
```

## 🔐 Segurança

O sistema implementa diversas medidas de segurança:

- Armazenamento seguro de senhas com hash e salt
- Proteção de rotas por nível de acesso
- Validação de dados em frontend e backend
- Proteção contra ataques comuns (SQL Injection, XSS)

## 📊 Classificação de Manchester

O sistema utiliza o Protocolo de Manchester para classificação de pacientes:

| Cor       | Prioridade     | Tempo Máximo |
|-----------|----------------|--------------|
| Vermelho  | Emergência     | Imediato     |
| Laranja   | Muito Urgente  | 10 minutos   |
| Amarelo   | Urgente        | 60 minutos   |
| Verde     | Pouco Urgente  | 120 minutos  |
| Azul      | Não Urgente    | 240 minutos  |

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 📞 Contato

Hospital de Clínicas de Ijuí - [https://hci.org.br/](https://hci.org.br/)

---

<div align="center">
  <p>Desenvolvido com ❤️ para o Hospital de Clínicas de Ijuí</p>
</div>
