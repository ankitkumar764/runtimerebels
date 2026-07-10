import logging
import json
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from app.core.memory import memory_manager
from app.core.verifier import verifier_agent, call_llm
from app.core.renderer import voice_renderer
from app.core.context import context_manager
from app.config import settings

logger = logging.getLogger(__name__)


# 1. State definition
class TwinState(TypedDict):
    query: str
    sender_id: str
    route: str
    evidence: str
    confidence: float
    raw_response: str
    final_response: List[str]


# 2. Classifier node
async def classifier_node(state: TwinState) -> Dict[str, Any]:
    query = state["query"]
    logger.info(f"Routing query: {query}")

    system_prompt = (
        "You are an routing classifier. Classify the user query into exactly one of three categories:\n"
        "- 'factual': A question asking for specific personal facts (e.g., Mom's name, college, place of birth, current employer, specific memories).\n"
        "- 'vibe': Conversational chat, opinions, feelings, jokes, greeting or general discussion.\n"
        "- 'unknown': Questions about facts you are completely unsure about or cannot answer.\n"
        "Respond in JSON format with exactly two fields:\n"
        '1. "route": one of "factual", "vibe", "unknown"\n'
        '2. "confidence": float between 0.0 and 1.0'
    )

    result_raw = await call_llm(system_prompt, query, temperature=0.0)

    route = "vibe"
    confidence = 1.0

    if result_raw:
        try:
            clean_json = result_raw.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            data = json.loads(clean_json)
            route = data.get("route", "vibe")
            confidence = data.get("confidence", 1.0)
        except Exception as e:
            logger.error(f"Error parsing classifier response: {e}. Raw: {result_raw}")

    # Fallback to simple matching if parsing fails or confidence is low
    if route not in ["factual", "vibe", "unknown"]:
        route = "vibe"

    logger.info(f"Classified route: {route} (confidence: {confidence})")
    return {"route": route, "confidence": confidence}


# 3. Factual path node
async def factual_node(state: TwinState) -> Dict[str, Any]:
    query = state["query"]

    # Retrieve from Identity Core first
    fact = memory_manager.get_identity_fact(query)
    evidence = fact if fact else ""

    # Retrieve from Qdrant temporal RAG memories
    qdrant_results = memory_manager.search_memories(query, top_k=3)
    qdrant_evidence = "\n".join([hit["text"] for hit in qdrant_results])

    combined_evidence = f"{evidence}\n{qdrant_evidence}".strip()
    logger.info(f"Retrieved evidence: {combined_evidence}")

    # Call Verifier
    verification = await verifier_agent.verify(query, combined_evidence)
    is_verified = verification.get("is_verified", False)
    confidence = verification.get("confidence", 0.0)
    summary = verification.get("summary", "")

    if not is_verified or confidence < 0.6:
        logger.info(
            f"Factual verification failed (verified: {is_verified}, confidence: {confidence}). Routing to Unknown deflection."
        )
        return {"route": "unknown", "evidence": ""}

    # Create raw answer based on evidence
    system_prompt = (
        "You are an assistant representing a user clone. Answer the query using ONLY the provided evidence.\n"
        "Do not invent facts outside the evidence. If the evidence is insufficient, say you don't know.\n"
        f"Evidence:\n{summary if summary else combined_evidence}"
    )

    raw_response = await call_llm(
        system_prompt, f"Question: {query}", temperature=0.2
    )
    if not raw_response:
        raw_response = f"Oh, that's: {summary}" if summary else "I think that is correct."

    return {"raw_response": raw_response, "evidence": combined_evidence}


# 4. Vibe path node
async def vibe_node(state: TwinState) -> Dict[str, Any]:
    query = state["query"]
    sender_id = state["sender_id"]

    # Fetch context history
    history = context_manager.get_context(sender_id)
    history_str = "\n".join([f"{h['role']}: {h['content']}" for h in history])

    system_prompt = (
        "You are a Digital Twin clone of the user. Reply to the chat message keeping their voice, tone, and vibes.\n"
        "Be conversational, opinionated, casual, and brief. Use slang if casual. Respond in character.\n"
        f"Recent conversation history:\n{history_str}"
    )

    raw_response = await call_llm(system_prompt, query, temperature=0.7)
    if not raw_response:
        raw_response = "Yeah for sure, vibe check passed."

    return {"raw_response": raw_response}


# 5. Unknown deflection node
async def unknown_node(state: TwinState) -> Dict[str, Any]:
    query = state["query"]
    logger.info("Routing through unknown deflection node...")

    # Pick a random deflection
    deflections = [
        "uhh not sure tbh",
        "lol idk man, let me check and get back to u",
        "hmmm not sure, i forgot haha",
        "idk about that one",
        "no clue tbh",
    ]
    raw_response = deflections[int(time_decay_hash(query)) % len(deflections)]
    return {"raw_response": raw_response}


# Helper hash function for deterministic randomness in deflection selection
def time_decay_hash(s: str) -> int:
    return sum(ord(c) for c in s)


# 6. Renderer node
async def renderer_node(state: TwinState) -> Dict[str, Any]:
    raw_response = state["raw_response"]
    sender_id = state["sender_id"]

    # Render through Voice Renderer using Formality settings
    final_response = voice_renderer.render(
        raw_response, formality_level=settings.FORMALITY_LEVEL
    )

    # Save to context manager history
    context_manager.add_turn(sender_id, "user", state["query"])
    for msg in final_response:
        context_manager.add_turn(sender_id, "assistant", msg)

    return {"final_response": final_response}


# 7. Routing decision function
def route_decision(state: TwinState) -> str:
    return state["route"]


# Define and Compile LangGraph StateGraph
workflow = StateGraph(TwinState)

# Add Nodes
workflow.add_node("classifier", classifier_node)
workflow.add_node("factual", factual_node)
workflow.add_node("vibe", vibe_node)
workflow.add_node("unknown", unknown_node)
workflow.add_node("renderer", renderer_node)

# Build Graph Edges
workflow.add_edge(START, "classifier")

workflow.add_conditional_edges(
    "classifier",
    route_decision,
    {
        "factual": "factual",
        "vibe": "vibe",
        "unknown": "unknown",
    },
)

# Route results to renderer
workflow.add_edge("factual", "renderer")
workflow.add_edge("vibe", "renderer")
workflow.add_edge("unknown", "renderer")
workflow.add_edge("renderer", END)

# Compile graph
graph = workflow.compile()
