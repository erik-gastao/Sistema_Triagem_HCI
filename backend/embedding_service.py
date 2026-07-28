import os
import json
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import List, Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("embedding_service.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("embedding_service")

class EmbeddingService:
    """
    Serviço otimizado para geração e gerenciamento de embeddings para o sistema de triagem.
    """
    
    def __init__(self, model_name: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Inicializa o serviço de embeddings.

        Args:
            model_name: Nome do modelo de embeddings a ser utilizado
            cache_dir: Diretório para cache de embeddings
        """
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "pucpr/biobertpt-clin")
        cache_dir = cache_dir or os.getenv("EMBEDDING_CACHE_DIR", "./embedding_cache")
        self.cache_dir = cache_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_cache = {}
        
        # Criar diretório de cache se não existir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            logger.info(f"Diretório de cache criado: {cache_dir}")
        
        # Carregar cache existente
        self._load_cache()
        
        # Inicializar modelo e tokenizer
        try:
            logger.info(f"Carregando modelo {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
            self.model.eval()  # Modo de avaliação para inferência
            logger.info(f"Modelo carregado com sucesso no dispositivo: {self.device}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {str(e)}")
            self.tokenizer = None
            self.model = None
            raise
    
    def _load_cache(self):
        """Carrega o cache de embeddings do disco."""
        cache_file = os.path.join(self.cache_dir, "embedding_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    # O cache armazena apenas os hashes dos textos, não os textos completos
                    self.embedding_cache = json.load(f)
                logger.info(f"Cache de embeddings carregado: {len(self.embedding_cache)} entradas")
            except Exception as e:
                logger.error(f"Erro ao carregar cache: {str(e)}")
                self.embedding_cache = {}
    
    def _save_cache(self):
        """Salva o cache de embeddings no disco."""
        cache_file = os.path.join(self.cache_dir, "embedding_cache.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.embedding_cache, f)
            logger.info(f"Cache de embeddings salvo: {len(self.embedding_cache)} entradas")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def _get_text_hash(self, text: str) -> str:
        """Gera um hash para o texto para uso como chave de cache."""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Gera embedding para um texto, utilizando cache quando disponível.
        
        Args:
            text: Texto para gerar embedding
            use_cache: Se deve utilizar cache
            
        Returns:
            Lista de floats representando o embedding
        """
        if not self.model or not self.tokenizer:
            logger.error("Modelo não inicializado")
            raise ValueError("Modelo não inicializado")
        
        # Verificar cache
        text_hash = self._get_text_hash(text)
        if use_cache and text_hash in self.embedding_cache:
            logger.debug(f"Embedding encontrado no cache para: {text[:30]}...")
            return self.embedding_cache[text_hash]
        
        # Gerar novo embedding
        try:
            logger.debug(f"Gerando novo embedding para: {text[:30]}...")
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Usar a representação do token [CLS] como embedding do texto
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0].tolist()
            
            # Salvar no cache
            if use_cache:
                self.embedding_cache[text_hash] = embedding
                # Salvar cache periodicamente (a cada 10 novos embeddings)
                if len(self.embedding_cache) % 10 == 0:
                    self._save_cache()
            
            return embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {str(e)}")
            raise
    
    def get_batch_embeddings(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos em lote.
        
        Args:
            texts: Lista de textos para gerar embeddings
            use_cache: Se deve utilizar cache
            
        Returns:
            Lista de embeddings
        """
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text, use_cache))
        return embeddings
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula a similaridade de cosseno entre dois textos.
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
            
        Returns:
            Valor de similaridade entre 0 e 1
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Converter para arrays numpy
        emb1_np = np.array(emb1)
        emb2_np = np.array(emb2)
        
        # Calcular similaridade de cosseno
        similarity = np.dot(emb1_np, emb2_np) / (np.linalg.norm(emb1_np) * np.linalg.norm(emb2_np))
        return float(similarity)
    
    def find_similar_texts(self, query_text: str, corpus: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Encontra os textos mais similares a um texto de consulta em um corpus.
        
        Args:
            query_text: Texto de consulta
            corpus: Lista de textos para comparar
            top_k: Número de resultados similares a retornar
            
        Returns:
            Lista de dicionários com texto e similaridade
        """
        query_embedding = self.get_embedding(query_text)
        
        similarities = []
        for i, text in enumerate(corpus):
            text_embedding = self.get_embedding(text)
            
            # Converter para arrays numpy
            query_np = np.array(query_embedding)
            text_np = np.array(text_embedding)
            
            # Calcular similaridade de cosseno
            similarity = np.dot(query_np, text_np) / (np.linalg.norm(query_np) * np.linalg.norm(text_np))
            similarities.append({
                "index": i,
                "text": text,
                "similarity": float(similarity)
            })
        
        # Ordenar por similaridade (decrescente)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Retornar os top_k mais similares
        return similarities[:top_k]
    
    def clear_cache(self):
        """Limpa o cache de embeddings."""
        self.embedding_cache = {}
        self._save_cache()
        logger.info("Cache de embeddings limpo")

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar serviço
    embedding_service = EmbeddingService()
    
    # Testar geração de embedding
    text = "Paciente com febre alta, tosse seca e dificuldade para respirar."
    embedding = embedding_service.get_embedding(text)
    print(f"Embedding gerado com {len(embedding)} dimensões")
    
    # Testar similaridade
    text1 = "Paciente com febre alta, tosse seca e dificuldade para respirar."
    text2 = "Paciente apresenta febre, tosse e falta de ar."
    similarity = embedding_service.compute_similarity(text1, text2)
    print(f"Similaridade entre os textos: {similarity:.4f}")
