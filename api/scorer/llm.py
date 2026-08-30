import os
import json
from typing import Dict, Any, Optional

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class LLMQualitativeJudge:
    """Uses the official Google GenAI SDK (Gemini Flash) or fallback heuristic to analyze textual artifacts (session.md, declaratif.md)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key and HAS_GENAI:
            self.client = genai.Client(api_key=self.api_key)

    async def analyze(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes qualitative textual artifacts."""
        session_text = profile_data.get("session")
        declaratif_text = profile_data.get("declaratif")

        if not session_text and not declaratif_text:
            return {
                "available": False,
                "reason": "Aucun document textuel qualitatif (session.md ou declaratif.md) fourni.",
            }

        # If LLM client is available, use it
        if self.client:
            try:
                return await self._call_gemini(session_text, declaratif_text)
            except Exception as e:
                # Fallback on heuristic if API call fails
                return self._heuristic_analysis(session_text, declaratif_text, error=str(e))

        return self._heuristic_analysis(session_text, declaratif_text)

    async def _call_gemini(self, session_text: Optional[str], declaratif_text: Optional[str]) -> Dict[str, Any]:
        prompt = f"""Tu es un évaluateur expert de la grille AIDD (AI-Driven Development).
Voici deux documents concernant un développeur :

---
DECLARATIF:
{declaratif_text or "Non fourni"}

---
SESSION DE TRAVAIL:
{session_text or "Non fournie"}

---
Analyse :
1. Qualité du cadrage et de l'intervention (Axe 3) : Est-ce du cadrage en amont, de la correction après coup, ou de l'autonomie ?
2. Incohérences déclaratives : Le développeur sur-estime-t-il ou sous-estime-t-il sa pratique ?
3. Recommandations prioritaires.

Réponds uniquement en JSON valide avec le schéma suivant :
{{
  "intervention_quality": "description concise",
  "cadrage_level": "faible | moyen | eleve",
  "inconsistencies": ["point 1", "point 2"],
  "llm_recommendations": ["conseil 1", "conseil 2"]
}}
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        # Clean potential markdown fences
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    @staticmethod
    def _heuristic_analysis(
        session_text: Optional[str], declaratif_text: Optional[str], error: Optional[str] = None
    ) -> Dict[str, Any]:
        inconsistencies = []
        cadrage_level = "moyen"
        intervention_quality = "Analyse heuristique des textes"

        if declaratif_text:
            d_lower = declaratif_text.lower()
            if "avancé" in d_lower or "haut du panier" in d_lower:
                inconsistencies.append("Auto-évaluation déclarative élevée nécessitant validation empirique.")
            if "copie les fichiers concernés directement dans la conversation" in d_lower:
                cadrage_level = "faible"
                intervention_quality = "Prompts conversationnels manuels sans contexte projet versionné."
            if "spec review" in d_lower or "cadrer et à relire" in d_lower:
                cadrage_level = "eleve"
                intervention_quality = "Cadrage rigoureux par spécifications préalables."

        if session_text:
            s_lower = session_text.lower()
            if "ne dévie pas" in s_lower or "spec dans" in s_lower:
                cadrage_level = "eleve"
                intervention_quality = "Délégation par contrat de spec avec checkpoints de validation."

        return {
            "available": True,
            "engine": "heuristic" if not error else f"fallback (error: {error})",
            "cadrage_level": cadrage_level,
            "intervention_quality": intervention_quality,
            "inconsistencies": inconsistencies,
            "llm_recommendations": [
                "Continuer à formaliser les instructions et spécifications en amont du code.",
            ],
        }
