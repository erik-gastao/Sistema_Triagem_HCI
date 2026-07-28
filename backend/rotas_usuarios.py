from fastapi import FastAPI, HTTPException, Depends, status, Request, Form, APIRouter
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime
import uuid
from usuarios import Usuario, init_users_db, criar_usuario, listar_usuarios, obter_usuario, atualizar_usuario, excluir_usuario, autenticar_usuario

# Criar router para usuários
router = APIRouter(prefix="/api", tags=["usuarios"])

# Modelos Pydantic
class UsuarioRequest(BaseModel):
    nome: str
    username: str
    password: str
    email: str
    role: str

class UsuarioUpdateRequest(BaseModel):
    nome: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    ativo: Optional[bool] = None

class UsuarioResponse(BaseModel):
    success: bool
    message: str
    id: Optional[str] = None

class UsuariosListResponse(BaseModel):
    usuarios: List[dict]

class UsuarioDetailResponse(BaseModel):
    success: bool
    usuario: Optional[dict] = None
    message: Optional[str] = None

# Inicializar banco de dados de usuários
init_users_db()

# Endpoints
@router.post("/usuarios", response_model=UsuarioResponse)
async def cadastrar_usuario(usuario: UsuarioRequest):
    """Cadastra um novo usuário no sistema"""
    try:
        novo_usuario = Usuario(
            nome=usuario.nome,
            username=usuario.username,
            password=usuario.password,
            email=usuario.email,
            role=usuario.role
        )
        
        resultado = criar_usuario(novo_usuario)
        
        if not resultado["success"]:
            raise HTTPException(status_code=400, detail=resultado["message"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar usuário: {str(e)}")

@router.get("/usuarios", response_model=UsuariosListResponse)
async def listar_todos_usuarios():
    """Lista todos os usuários cadastrados"""
    try:
        usuarios = listar_usuarios()
        return {"usuarios": usuarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@router.get("/usuarios/{usuario_id}", response_model=UsuarioDetailResponse)
async def obter_detalhes_usuario(usuario_id: str):
    """Obtém os detalhes de um usuário específico"""
    try:
        resultado = obter_usuario(usuario_id)
        
        if not resultado["success"]:
            raise HTTPException(status_code=404, detail=resultado["message"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter usuário: {str(e)}")

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def atualizar_dados_usuario(usuario_id: str, dados: UsuarioUpdateRequest):
    """Atualiza os dados de um usuário"""
    try:
        resultado = atualizar_usuario(usuario_id, dados.model_dump(exclude_unset=True))
        
        if not resultado["success"]:
            raise HTTPException(status_code=400, detail=resultado["message"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")

@router.delete("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def excluir_usuario_sistema(usuario_id: str):
    """Exclui um usuário do sistema"""
    try:
        resultado = excluir_usuario(usuario_id)
        
        if not resultado["success"]:
            raise HTTPException(status_code=404, detail=resultado["message"])
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir usuário: {str(e)}")

# Atualizar endpoint de login para usar o novo sistema de autenticação
@router.post("/login")
async def login(request: Request):
    """Autentica um usuário no sistema"""
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return {"success": False, "message": "Usuário e senha são obrigatórios"}
        
        resultado = autenticar_usuario(username, password)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar login: {str(e)}")
