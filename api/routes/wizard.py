"""Endpoint do Wizard — chat conversacional com RAG."""

from fastapi import APIRouter, HTTPException
from api.models import ChatMessage, WizardResponse, ToolSolution
import api.rag as _rag
from api.rag import query_catalog, build_prompt
from api.routing import extract_recommendation

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


@router.post("/chat", response_model=WizardResponse)
def wizard_chat(msg: ChatMessage):
    """Process a chat message through the RAG pipeline and return a response.

    1. Validate message (Pydantic handles min_length=1; whitespace-only caught here).
    2. Semantic search in ChromaDB for similar projects.
    3. Build augmented prompt and call Ollama LLM.
    4. Extract tool recommendation from LLM response.
    5. Return structured WizardResponse.
    """
    # Extra whitespace-only guard (Pydantic min_length=1 catches empty strings,
    # but a single space passes — we reject pure whitespace explicitly)
    if not msg.message.strip():
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode ser vazia ou conter apenas espaços.",
        )

    # Step 1: Semantic search
    try:
        similar_projects = query_catalog(msg.message)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Serviço de busca indisponível.",
        )

    # Step 2: Build prompt and call LLM
    prompt = build_prompt(msg.message, similar_projects)
    try:
        llm_answer = _rag._llm_client.generate(prompt)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Modelo LLM não encontrado. Verifique LLAMA_MODEL_PATH.",
        )
    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Serviço LLM local indisponível. Verifique se o Ollama está em execução.",
        )
    except TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Tempo de resposta excedido.",
        )

    # Step 3: Extract recommendation
    recommendation = extract_recommendation(llm_answer)

    # Build response
    rec_tool = recommendation.tool if recommendation.tool != ToolSolution.NO_SOLUTION else None
    justification = recommendation.justification

    # If no solution, adjust the answer
    if recommendation.tool == ToolSolution.NO_SOLUTION:
        if "não temos" not in llm_answer.lower():
            llm_answer += (
                "\n\nNão temos uma solução disponível hoje para esta demanda. "
                "Sugerimos registrar como nova demanda de inovação."
            )

    return WizardResponse(
        answer=llm_answer,
        recommended_tool=rec_tool if rec_tool else recommendation.tool,
        justification=justification,
        similar_projects=similar_projects,
    )
