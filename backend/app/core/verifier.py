import json
import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)


async def call_llm(
    system_prompt: str, user_prompt: str, temperature: float = 0.0
) -> Optional[str]:
    """Helper function to call Groq or fallback to Together AI."""
    # 1. Try Groq
    if settings.GROQ_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": 500,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return (
                        response.json()
                        .get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                    )
                else:
                    logger.warning(
                        f"Groq API returned error {response.status_code}: {response.text}"
                    )
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")

    # 2. Fallback to Together AI
    if settings.TOGETHER_API_KEY:
        logger.info("Attempting Together AI fallback...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.together.xyz/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": 500,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return (
                        response.json()
                        .get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                    )
                else:
                    logger.warning(
                        f"Together AI returned error {response.status_code}: {response.text}"
                    )
        except Exception as e:
            logger.error(f"Error calling Together AI API: {e}")

    # 3. Local Mock Fallback for demos/testing when keys are not provided
    logger.warning("No API keys worked or were configured. Using Mock fallback.")
    return None


class VerifierAgent:
    """Verifies if the retrieved facts/RAG evidence answers the user's factual query."""

    async def verify(self, query: str, evidence: str) -> Dict[str, Any]:
        if not evidence or len(evidence.strip()) == 0:
            return {"is_verified": False, "confidence": 0.0, "reason": "No evidence provided."}

        system_prompt = (
            "You are a factual verifier. Compare the USER QUERY with the provided EVIDENCE.\n"
            "Determine if the evidence contains the direct facts needed to answer the query.\n"
            "Respond in JSON format with exactly three fields:\n"
            '1. "is_verified": boolean (true if evidence answers query, false otherwise)\n'
            '2. "confidence": float between 0.0 and 1.0 (how sure you are)\n'
            '3. "summary": string (a short summary of the fact if verified, or empty string)'
        )

        user_prompt = f"USER QUERY: {query}\n\nEVIDENCE:\n{evidence}"

        raw_result = await call_llm(
            system_prompt, user_prompt, temperature=0.0
        )

        if not raw_result:
            # Mock verification behavior if keys are missing
            is_valid = "name" in query.lower() or "mom" in query.lower()
            return {
                "is_verified": is_valid,
                "confidence": 0.9 if is_valid else 0.2,
                "summary": "Mock fact resolution" if is_valid else "",
            }

        try:
            # Extract JSON from potential markdown blocks
            clean_json = raw_result.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Failed to parse Verifier response: {e}. Raw: {raw_result}")
            return {
                "is_verified": False,
                "confidence": 0.0,
                "summary": "",
                "error": "Failed to parse json",
            }


verifier_agent = VerifierAgent()
