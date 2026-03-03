"""
Serviço de Análise de Bugs com IA
Utiliza Google Generative AI (Gemini) para analisar reportes de bugs
"""
import json
import logging
import os
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    Serviço para análise automática de bugs usando IA
    Analisa logs do console, URL e comentários do usuário
    """

    def __init__(self):
        """Inicializa o cliente do Google Generative AI"""
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_AI_API_KEY não configurada. Análise de IA desabilitada.")
            self.client = None
            return

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel("gemini-pro")

    def analyze_bug(
        self,
        comment: str,
        console_logs: Optional[str] = None,
        page_url: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analisa um reporte de bug usando IA

        Args:
            comment: Comentário do usuário sobre o bug
            console_logs: Logs do console do navegador (JSON string)
            page_url: URL da página onde o bug ocorreu
            user_agent: User agent do navegador

        Returns:
            Dict com: {
                "summary": str,
                "steps_to_reproduce": List[str],
                "severity": "low" | "medium" | "high" | "critical",
                "affected_components": List[str],
                "suggested_fix": str
            }
            Ou None se não conseguir analisar
        """
        if not self.client:
            logger.warning("Cliente IA não disponível")
            return None

        try:
            # Construir prompt estruturado
            prompt = self._build_prompt(comment, console_logs, page_url, user_agent)

            # Fazer requisição para IA
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1024,
                ),
            )

            # Extrair resposta
            if not response.text:
                logger.warning("Resposta vazia da IA")
                return None

            # Parsear JSON da resposta
            analysis = self._parse_ai_response(response.text)
            return analysis

        except Exception as exc:
            logger.error(f"Erro ao analisar bug com IA: {str(exc)}")
            return None

    def _build_prompt(
        self,
        comment: str,
        console_logs: Optional[str] = None,
        page_url: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Constrói o prompt para enviar à IA"""
        prompt = f"""
Você é um especialista em análise de bugs e QA. Analise o seguinte reporte de bug e retorne uma análise estruturada em JSON.

## Informações do Bug:

**Comentário do Usuário:**
{comment}

"""

        if page_url:
            prompt += f"**URL da Página:** {page_url}\n\n"

        if user_agent:
            prompt += f"**User Agent:** {user_agent}\n\n"

        if console_logs:
            prompt += f"**Logs do Console:**\n```\n{console_logs}\n```\n\n"

        prompt += """
## Instruções:

Retorne APENAS um JSON válido (sem markdown ou código blocks) com a seguinte estrutura:
{
    "summary": "Resumo técnico conciso do bug (máximo 150 caracteres)",
    "steps_to_reproduce": [
        "Passo 1 para reproduzir",
        "Passo 2 para reproduzir",
        "Passo 3 para reproduzir"
    ],
    "severity": "low|medium|high|critical",
    "affected_components": [
        "Nome do componente 1",
        "Nome do componente 2"
    ],
    "suggested_fix": "Sugestão de correção técnica baseada na análise"
}

Critérios de severidade:
- "critical": Impede completamente a funcionalidade, afeta múltiplos usuários
- "high": Funcionalidade importante quebrada, afeta conversão/vendas
- "medium": Funcionalidade parcialmente quebrada, não crítica para vendas
- "low": Pequeno problema visual ou funcionalidade secundária

Responda APENAS com o JSON, sem explicações adicionais.
"""
        return prompt

    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extrai JSON válido da resposta da IA

        Args:
            response_text: Texto da resposta da IA

        Returns:
            Dict parseado ou None se inválido
        """
        try:
            # Tentar parsear diretamente
            analysis = json.loads(response_text)

            # Validar campos obrigatórios
            required_fields = ["summary", "steps_to_reproduce", "severity"]
            if not all(field in analysis for field in required_fields):
                logger.warning("Resposta da IA falta campos obrigatórios")
                return None

            # Validar valores de severity
            if analysis["severity"] not in ["low", "medium", "high", "critical"]:
                logger.warning(f"Severity inválida: {analysis['severity']}")
                analysis["severity"] = "medium"  # Default

            # Garantir que steps_to_reproduce é lista
            if not isinstance(analysis.get("steps_to_reproduce"), list):
                analysis["steps_to_reproduce"] = []

            # Garantir que affected_components é lista
            if not isinstance(analysis.get("affected_components"), list):
                analysis["affected_components"] = []

            return analysis

        except json.JSONDecodeError as exc:
            logger.error(f"Erro ao parsear JSON da resposta IA: {str(exc)}")
            # Tentar extrair JSON de um texto que pode ter markdown
            try:
                # Procurar por ``` e extrair o conteúdo
                if "```json" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    json_str = response_text[start:end].strip()
                    return json.loads(json_str)
                elif "```" in response_text:
                    start = response_text.find("```") + 3
                    end = response_text.find("```", start)
                    json_str = response_text[start:end].strip()
                    return json.loads(json_str)
                elif "{" in response_text:
                    # Procurar por { e }
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                logger.error("Não foi possível extrair JSON da resposta IA")
                return None

            return None
