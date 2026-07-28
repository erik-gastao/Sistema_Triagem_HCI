import asyncio
import logging
import os
from typing import List, Optional, Tuple

import httpx

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_service")
handler = logging.FileHandler("ollama_service.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

CLASSIFICACOES = ("VERMELHO", "LARANJA", "AMARELO", "VERDE", "AZUL")


class OllamaService:
    def __init__(
        self,
        url: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 120.0,
    ):
        self.url = (url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.max_retries = max_retries
        self.timeout = timeout
        logger.info(f"Serviço Ollama inicializado: url={self.url}, modelo={self.model}, max_retries={max_retries}")

    async def is_available(self) -> bool:
        """Verifica se o servidor Ollama responde."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama indisponível: {e}")
            return False

    async def generate_response(self, prompt: str) -> str:
        """Envia um prompt já formatado ao Ollama e devolve o texto gerado."""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Enviando prompt para Ollama (tentativa {attempt}/{self.max_retries})")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.url}/api/generate",
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {
                                "temperature": 0.2,
                                "top_p": 0.9,
                            },
                        },
                    )

                if response.status_code == 200:
                    response_text = response.json().get("response", "")
                    logger.info(f"Resposta gerada com sucesso: {len(response_text)} caracteres")
                    return response_text

                logger.error(f"Erro na API Ollama: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Erro ao chamar API Ollama: {str(e)}")

            # Esperar antes de tentar novamente (backoff exponencial)
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Aguardando {wait_time}s antes da próxima tentativa...")
                await asyncio.sleep(wait_time)

        # Se todas as tentativas falharem, retornar uma resposta de fallback
        logger.error("Todas as tentativas de chamar a API Ollama falharam")
        return self._generate_fallback_response()

    def format_prompt(self, symptoms: str, similar_cases: Optional[List[dict]] = None) -> str:
        """Monta o prompt de triagem, incluindo casos validados semelhantes quando houver."""
        return f"""Você é um sistema especializado em triagem hospitalar baseado no Protocolo de Manchester.

Sua tarefa é analisar os sintomas do paciente e fornecer:
1. Uma classificação de urgência (VERMELHO, LARANJA, AMARELO, VERDE ou AZUL)
2. Uma análise clínica em tópicos curtos e objetivos
3. Condutas recomendadas em formato de lista numerada

PROTOCOLO DE MANCHESTER:
- VERMELHO (Emergência): Risco imediato à vida. Atendimento imediato.
- LARANJA (Muito Urgente): Risco alto. Atendimento em até 10 minutos.
- AMARELO (Urgente): Risco moderado. Atendimento em até 60 minutos.
- VERDE (Pouco Urgente): Risco baixo. Atendimento em até 120 minutos.
- AZUL (Não Urgente): Sem risco. Atendimento em até 240 minutos.
{self._format_similar_cases(similar_cases)}
SINTOMAS DO PACIENTE:
{symptoms}

Forneça sua resposta no seguinte formato exato:

CLASSIFICAÇÃO: [COR]

ANÁLISE CLÍNICA:
[Ponto principal 1 - máximo 15 palavras]
[Ponto principal 2 - máximo 15 palavras]
[Ponto principal 3 - máximo 15 palavras]
[Ponto principal 4 - máximo 15 palavras]

CONDUTAS RECOMENDADAS:
[Conduta 1 - máximo 15 palavras]
[Conduta 2 - máximo 15 palavras]
[Conduta 3 - máximo 15 palavras]
[Conduta 4 - máximo 15 palavras]
[Conduta 5 - máximo 15 palavras]

IMPORTANTE: Seja extremamente conciso. Use apenas tópicos curtos com informações essenciais. Evite frases longas e explicações detalhadas. NÃO INCLUA MARCADORES (•, *, números) no início dos tópicos.
"""

    def _format_similar_cases(self, similar_cases: Optional[List[dict]]) -> str:
        """Formata os casos validados semelhantes como referência para o modelo."""
        if not similar_cases:
            return ""

        blocos = []
        for i, caso in enumerate(similar_cases, start=1):
            sintomas = (caso.get("sintomas") or "").strip()
            classificacao = (caso.get("classificacao") or "").strip()
            if not sintomas:
                continue
            linha = f"Caso {i} - Sintomas: {sintomas}"
            if classificacao:
                linha += f"\n  Classificação validada: {classificacao}"
            blocos.append(linha)

        if not blocos:
            return ""

        casos_texto = "\n".join(blocos)
        return (
            "\nCASOS SEMELHANTES JÁ VALIDADOS POR PROFISSIONAIS DESTE HOSPITAL:\n"
            f"{casos_texto}\n"
            "Use estes casos apenas como referência de calibragem. "
            "Se os sintomas atuais forem mais graves, classifique com prioridade maior.\n"
        )

    def _generate_fallback_response(self) -> str:
        """Gera uma resposta de fallback quando a API Ollama falha."""
        return """CLASSIFICAÇÃO: AMARELO

ANÁLISE CLÍNICA:
Não foi possível realizar uma análise detalhada devido a problemas técnicos. Por precaução, o paciente recebeu classificação AMARELO (Urgente).

CONDUTAS RECOMENDADAS:
1. Avaliação médica em até 60 minutos
2. Monitoramento de sinais vitais
3. Reavaliação da classificação por profissional de saúde
4. Documentação do caso como incidente técnico
5. Verificação manual dos sintomas relatados"""

    def parse_response(self, response: str) -> Tuple[str, str, str]:
        """Analisa a resposta do modelo para extrair classificação, justificativa e condutas."""
        try:
            # Extrair classificação
            classification = ""
            if "CLASSIFICAÇÃO:" in response:
                classification_line = response.split("CLASSIFICAÇÃO:")[1].split("\n")[0].upper()
                for cor in CLASSIFICACOES:
                    if cor in classification_line:
                        classification = cor
                        break

            # Extrair justificativa
            justification = ""
            if "ANÁLISE CLÍNICA:" in response:
                parts = response.split("ANÁLISE CLÍNICA:")[1].split("CONDUTAS RECOMENDADAS:")
                justification = parts[0].strip()

            # Extrair condutas
            recommendations = ""
            if "CONDUTAS RECOMENDADAS:" in response:
                recommendations = response.split("CONDUTAS RECOMENDADAS:")[1].strip()

            logger.info(
                f"Resposta processada: classificação={classification}, "
                f"justificativa={len(justification)} caracteres, condutas={len(recommendations)} caracteres"
            )
            return classification, justification, recommendations
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {str(e)}")
            return "AMARELO", "", ""  # Fallback para classificação AMARELO em caso de erro
