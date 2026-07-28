import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importar serviços otimizados
from embedding_service import EmbeddingService
from ollama_service import OllamaService

# Importar módulos de usuários
from rotas_usuarios import router as usuarios_router

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./validacao_triagem.db")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "triagem_hci")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
N_CASOS_SIMILARES = int(os.getenv("N_CASOS_SIMILARES", "3"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("triagem_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("triagem_api")

# Initialize FastAPI app
app = FastAPI(
    title="Sistema de Triagem API",
    description="API para o Sistema de Triagem baseado no Protocolo de Manchester",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas de usuários
app.include_router(usuarios_router)

# Inicializar serviços
try:
    embedding_service = EmbeddingService()
    logger.info("Serviço de embeddings inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar serviço de embeddings: {str(e)}")
    embedding_service = None

try:
    ollama_service = OllamaService()
    logger.info("Serviço Ollama inicializado com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar serviço Ollama: {str(e)}")
    ollama_service = None

# Initialize ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    logger.info(f"Coleção ChromaDB '{COLLECTION_NAME}' pronta ({collection.count()} documentos)")
except Exception as e:
    logger.error(f"Erro ao inicializar ChromaDB: {str(e)}")
    collection = None


# Pydantic models
class TriagemProcessar(BaseModel):
    sintomas: str


class TriagemResponse(BaseModel):
    id: str
    sintomas: str
    resposta: str
    classificacao: str
    justificativa: str
    condutas: str
    data_hora: str
    casos_similares: int = 0


class ValidationRequest(BaseModel):
    triagem_id: str
    validado_por: str
    feedback: str
    classificacao_corrigida: Optional[str] = None


class ValidationResponse(BaseModel):
    success: bool
    message: str


# Database functions
@contextmanager
def get_conn():
    """Abre uma conexão SQLite, garantindo commit/rollback e fechamento."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_validation_db():
    with get_conn() as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS validacao_triagem (
            id TEXT PRIMARY KEY,
            sintomas TEXT NOT NULL,
            resposta TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            validado INTEGER DEFAULT 0,
            feedback TEXT,
            validado_por TEXT,
            data_validacao TEXT,
            classificacao TEXT,
            justificativa TEXT,
            condutas TEXT
        )
        ''')
    logger.info("Banco de dados de validação inicializado")


def salvar_para_validacao(sintomas, resposta, classificacao="", justificativa="", condutas=""):
    triagem_id = str(uuid.uuid4())
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO validacao_triagem (id, sintomas, resposta, data_hora, classificacao, justificativa, condutas)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (triagem_id, sintomas, str(resposta), data_hora, classificacao, justificativa, condutas)
        )
    logger.info(f"Triagem salva para validação: id={triagem_id}")
    return triagem_id


def carregar_casos_validados():
    """Retorna os casos já validados, com id estável para uso no ChromaDB."""
    try:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, sintomas, resposta, classificacao FROM validacao_triagem WHERE validado = 1"
            ).fetchall()
        logger.info(f"Casos validados carregados: {len(rows)} casos")
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Erro ao carregar casos validados: {str(e)}")
        return []


def indexar_caso_validado(caso: dict) -> bool:
    """Insere/atualiza um caso validado no ChromaDB usando o id da triagem como chave."""
    if collection is None or embedding_service is None:
        return False
    try:
        embedding = embedding_service.get_embedding(caso["sintomas"])
        collection.upsert(
            ids=[caso["id"]],
            embeddings=[embedding],
            metadatas=[{
                "sintomas": caso["sintomas"],
                "resposta": caso.get("resposta") or "",
                "classificacao": caso.get("classificacao") or "",
            }],
        )
        logger.info(f"Caso validado indexado no ChromaDB: id={caso['id']}")
        return True
    except Exception as e:
        logger.error(f"Erro ao indexar caso validado {caso.get('id')}: {str(e)}")
        return False


def obter_triagens(filtro="todas"):
    query = (
        "SELECT id, sintomas, resposta, data_hora, validado, feedback, validado_por,"
        " data_validacao, classificacao, justificativa, condutas FROM validacao_triagem"
    )

    if filtro == "pendentes":
        query += " WHERE validado = 0"
    elif filtro == "validadas":
        query += " WHERE validado = 1"

    query += " ORDER BY data_hora DESC"

    with get_conn() as conn:
        rows = conn.execute(query).fetchall()

    result = [dict(row) for row in rows]
    logger.info(f"Triagens obtidas: {len(result)} triagens (filtro: {filtro})")
    return result


def validar_triagem(triagem_id, validado_por, feedback, classificacao_corrigida=None):
    """Marca a triagem como validada e devolve o caso atualizado (ou None se não existir)."""
    data_validacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        if classificacao_corrigida:
            cursor = conn.execute(
                "UPDATE validacao_triagem SET validado = 1, feedback = ?, validado_por = ?,"
                " data_validacao = ?, classificacao = ? WHERE id = ?",
                (feedback, validado_por, data_validacao, classificacao_corrigida, triagem_id)
            )
        else:
            cursor = conn.execute(
                "UPDATE validacao_triagem SET validado = 1, feedback = ?, validado_por = ?,"
                " data_validacao = ? WHERE id = ?",
                (feedback, validado_por, data_validacao, triagem_id)
            )

        if cursor.rowcount == 0:
            return None

        row = conn.execute(
            "SELECT id, sintomas, resposta, classificacao FROM validacao_triagem WHERE id = ?",
            (triagem_id,)
        ).fetchone()

    logger.info(f"Triagem validada: id={triagem_id}, validado_por={validado_por}")
    return dict(row) if row else None


def buscar_casos_similares(sintomas: str) -> List[dict]:
    """Busca no ChromaDB os casos validados mais parecidos com os sintomas informados."""
    if collection is None or embedding_service is None or collection.count() == 0:
        return []

    try:
        query_embedding = embedding_service.get_embedding(sintomas)
        n_results = min(N_CASOS_SIMILARES, collection.count())
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results)

        metadatas = (results.get("metadatas") or [[]])[0]
        casos = [
            {
                "sintomas": m.get("sintomas", ""),
                "classificacao": m.get("classificacao", ""),
            }
            for m in metadatas
            if m.get("sintomas")
        ]
        logger.info(f"Casos similares encontrados: {len(casos)}")
        return casos
    except Exception as e:
        logger.error(f"Erro ao buscar casos similares: {str(e)}")
        return []


# Initialize database
init_validation_db()

# Indexar casos já validados no banco vetorial (upsert por id, sem duplicar entre reinícios)
for caso in carregar_casos_validados():
    indexar_caso_validado(caso)


# API endpoints
@app.get("/")
async def root():
    return {"message": "Sistema de Triagem API"}


@app.post("/api/triagem", response_model=TriagemResponse)
async def realizar_triagem(request: TriagemProcessar):
    try:
        # Check if symptoms are provided
        if not request.sintomas or not request.sintomas.strip():
            logger.warning("Requisição de triagem sem sintomas")
            raise HTTPException(status_code=400, detail="Sintomas não fornecidos")

        logger.info(f"Iniciando triagem: {request.sintomas[:50]}...")

        if ollama_service is None:
            logger.error("Serviço Ollama não disponível")
            raise HTTPException(status_code=503, detail="Serviço Ollama não disponível")

        # Recuperar casos validados semelhantes (RAG). Falha aqui não impede a triagem.
        casos_similares = buscar_casos_similares(request.sintomas)

        # Montar prompt com os casos semelhantes e gerar a resposta
        prompt = ollama_service.format_prompt(request.sintomas, casos_similares)
        response_text = await ollama_service.generate_response(prompt)
        logger.info(f"Resposta gerada: {len(response_text)} caracteres")

        classificacao, justificativa, condutas = ollama_service.parse_response(response_text)
        logger.info(f"Resposta processada: classificação={classificacao}")

        # Save to validation database
        triagem_id = salvar_para_validacao(
            request.sintomas,
            response_text,
            classificacao,
            justificativa,
            condutas
        )

        return {
            "id": triagem_id,
            "sintomas": request.sintomas,
            "resposta": response_text,
            "classificacao": classificacao,
            "justificativa": justificativa,
            "condutas": condutas,
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "casos_similares": len(casos_similares),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar triagem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar triagem: {str(e)}")


@app.get("/api/triagens")
async def listar_triagens(filtro: str = "todas"):
    try:
        return {"triagens": obter_triagens(filtro)}
    except Exception as e:
        logger.error(f"Erro ao listar triagens: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar triagens: {str(e)}")


@app.post("/api/validar", response_model=ValidationResponse)
async def validar(request: ValidationRequest):
    try:
        caso = validar_triagem(
            request.triagem_id,
            request.validado_por,
            request.feedback,
            request.classificacao_corrigida,
        )
        if caso is None:
            raise HTTPException(status_code=404, detail="Triagem não encontrada")

        # Alimenta o banco vetorial na hora, para as próximas triagens já aproveitarem o caso
        indexar_caso_validado(caso)

        return {"success": True, "message": "Triagem validada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao validar triagem: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao validar triagem: {str(e)}")


@app.get("/api/estatisticas")
async def estatisticas():
    try:
        with get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM validacao_triagem").fetchone()[0]
            validadas = conn.execute("SELECT COUNT(*) FROM validacao_triagem WHERE validado = 1").fetchone()[0]

        return {
            "total": total,
            "validadas": validadas,
            "pendentes": total - validadas,
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")


@app.get("/api/status")
async def status():
    """Endpoint para verificar o status dos serviços"""
    try:
        status_data = {
            "api": "online",
            "embedding_service": "online" if embedding_service is not None else "offline",
            "ollama_service": "online" if ollama_service is not None else "offline",
            "chromadb": "online" if collection is not None else "offline",
            "database": "online",
            "casos_indexados": collection.count() if collection is not None else 0,
        }

        if ollama_service is not None:
            status_data["ollama_available"] = await ollama_service.is_available()
            status_data["ollama_model"] = ollama_service.model

        return status_data
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return {"api": "degraded", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
