import sqlite3
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
import os
import uuid

DB_PATH = os.getenv("DB_PATH", "./validacao_triagem.db")

# Modelo de dados para usuários
class Usuario(BaseModel):
    id: Optional[str] = None
    nome: str
    username: str
    password: str
    email: str
    role: str
    data_criacao: Optional[str] = None
    ativo: Optional[bool] = True

# Função para criar hash de senha
def hash_password(password: str) -> str:
    """Cria um hash seguro da senha fornecida"""
    salt = uuid.uuid4().hex
    hashed = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return f"{salt}${hashed}"

# Função para verificar senha
def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado"""
    salt, hashed = stored_password.split('$')
    verify_hash = hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()
    return verify_hash == hashed

# Inicialização da tabela de usuários
def init_users_db():
    """Inicializa a tabela de usuários no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        data_criacao TEXT NOT NULL,
        ativo INTEGER DEFAULT 1
    )
    ''')
    
    # Verificar se já existem usuários padrão
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    
    # Se não existirem usuários, criar os padrões
    if count == 0:
        # Criar usuários padrão
        admin_id = str(uuid.uuid4())
        medico_id = str(uuid.uuid4())
        enfermeiro_id = str(uuid.uuid4())
        
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Admin
        cursor.execute(
            "INSERT INTO usuarios (id, nome, username, password, email, role, data_criacao, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (admin_id, "Administrador", "admin", hash_password("admin"), "admin@hci.org.br", "admin", data_criacao, 1)
        )
        
        # Médico
        cursor.execute(
            "INSERT INTO usuarios (id, nome, username, password, email, role, data_criacao, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (medico_id, "Médico Demonstração", "medico", hash_password("medico"), "medico@hci.org.br", "medico", data_criacao, 1)
        )
        
        # Enfermeiro
        cursor.execute(
            "INSERT INTO usuarios (id, nome, username, password, email, role, data_criacao, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (enfermeiro_id, "Enfermeiro Demonstração", "enfermeiro", hash_password("enfermeiro"), "enfermeiro@hci.org.br", "enfermeiro", data_criacao, 1)
        )
    
    conn.commit()
    conn.close()

# Funções para gerenciamento de usuários
def criar_usuario(usuario: Usuario) -> dict:
    """Cria um novo usuário no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o username já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = ?", (usuario.username,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {"success": False, "message": "Nome de usuário já existe"}
        
        # Verificar se o email já existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ?", (usuario.email,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {"success": False, "message": "Email já cadastrado"}
        
        # Gerar ID e data de criação
        usuario_id = str(uuid.uuid4())
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Hash da senha
        hashed_password = hash_password(usuario.password)
        
        # Inserir usuário
        cursor.execute(
            "INSERT INTO usuarios (id, nome, username, password, email, role, data_criacao, ativo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario_id, usuario.nome, usuario.username, hashed_password, usuario.email, usuario.role, data_criacao, 1)
        )
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Usuário criado com sucesso", "id": usuario_id}
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"success": False, "message": f"Erro ao criar usuário: {str(e)}"}

def listar_usuarios() -> list:
    """Lista todos os usuários cadastrados"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, username, email, role, data_criacao, ativo FROM usuarios ORDER BY nome")
    usuarios = cursor.fetchall()
    
    conn.close()
    
    result = []
    for usuario in usuarios:
        result.append({
            "id": usuario[0],
            "nome": usuario[1],
            "username": usuario[2],
            "email": usuario[3],
            "role": usuario[4],
            "data_criacao": usuario[5],
            "ativo": bool(usuario[6])
        })
    
    return result

def obter_usuario(usuario_id: str) -> dict:
    """Obtém os detalhes de um usuário específico"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, username, email, role, data_criacao, ativo FROM usuarios WHERE id = ?", (usuario_id,))
    usuario = cursor.fetchone()
    
    conn.close()
    
    if not usuario:
        return {"success": False, "message": "Usuário não encontrado"}
    
    return {
        "success": True,
        "usuario": {
            "id": usuario[0],
            "nome": usuario[1],
            "username": usuario[2],
            "email": usuario[3],
            "role": usuario[4],
            "data_criacao": usuario[5],
            "ativo": bool(usuario[6])
        }
    }

def atualizar_usuario(usuario_id: str, dados: dict) -> dict:
    """Atualiza os dados de um usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o usuário existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id = ?", (usuario_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"success": False, "message": "Usuário não encontrado"}
        
        # Construir a query de atualização
        update_fields = []
        params = []
        
        if "nome" in dados:
            update_fields.append("nome = ?")
            params.append(dados["nome"])
        
        if "email" in dados:
            # Verificar se o email já existe para outro usuário
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = ? AND id != ?", (dados["email"], usuario_id))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return {"success": False, "message": "Email já cadastrado para outro usuário"}
            
            update_fields.append("email = ?")
            params.append(dados["email"])
        
        if "password" in dados and dados["password"]:
            update_fields.append("password = ?")
            params.append(hash_password(dados["password"]))
        
        if "role" in dados:
            update_fields.append("role = ?")
            params.append(dados["role"])
        
        if "ativo" in dados:
            update_fields.append("ativo = ?")
            params.append(1 if dados["ativo"] else 0)
        
        if not update_fields:
            conn.close()
            return {"success": False, "message": "Nenhum campo para atualizar"}
        
        # Executar a atualização
        query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
        params.append(usuario_id)
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Usuário atualizado com sucesso"}
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"success": False, "message": f"Erro ao atualizar usuário: {str(e)}"}

def excluir_usuario(usuario_id: str) -> dict:
    """Exclui um usuário do sistema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se o usuário existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id = ?", (usuario_id,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return {"success": False, "message": "Usuário não encontrado"}
        
        # Excluir o usuário
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Usuário excluído com sucesso"}
    
    except Exception as e:
        conn.rollback()
        conn.close()
        return {"success": False, "message": f"Erro ao excluir usuário: {str(e)}"}

def autenticar_usuario(username: str, password: str) -> dict:
    """Autentica um usuário com base no username e senha"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password, role, ativo FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    
    conn.close()
    
    if not usuario:
        return {"success": False, "message": "Usuário não encontrado"}
    
    if not bool(usuario[4]):
        return {"success": False, "message": "Usuário inativo"}
    
    if verify_password(usuario[2], password):
        return {
            "success": True, 
            "message": "Autenticação bem-sucedida",
            "user": usuario[1],
            "role": usuario[3]
        }
    else:
        return {"success": False, "message": "Senha incorreta"}
