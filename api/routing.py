"""Lógica de roteamento: mapeia resposta do LLM para uma ToolSolution."""

import re
from api.models import ToolSolution

# Mapping of keywords/phrases to ToolSolution values
TOOL_KEYWORDS: dict[ToolSolution, list[str]] = {
    ToolSolution.COPILOT: ["copilot", "github copilot", "co-pilot"],
    ToolSolution.LOVABLE: ["lovable"],
    ToolSolution.N8N: ["n8n"],
    ToolSolution.ALTERYX: ["alteryx"],
    ToolSolution.BI_TEAM: ["equipe bi", "bi team", "time bi", "time de bi"],
    ToolSolution.DEEP_TEAM: ["equipe deep", "deep team", "time deep"],
    ToolSolution.SQUAD: ["squad", "desenvolvimento squad", "squad de desenvolvimento"],
    ToolSolution.NO_SOLUTION: [
        "não temos uma solução",
        "não temos solução",
        "no solution",
        "sem solução",
        "nenhuma solução",
    ],
}

AVAILABLE_TOOLS: list[str] = [
    "Copilot", "Lovable", "n8n", "Alteryx",
    "Equipe Deep", "Equipe BI", "Squad de Desenvolvimento",
    "Não temos uma solução disponível hoje",
]


class ToolRecommendation:
    """Result of extracting a tool recommendation from LLM output."""

    def __init__(self, tool: ToolSolution, justification: str):
        self.tool = tool
        self.justification = justification


def extract_recommendation(llm_response: str) -> ToolRecommendation:
    """Extract a tool recommendation from the LLM response text.

    Strategy:
    1. Look for explicit "RECOMENDAÇÃO: <tool>" pattern first.
    2. Fall back to keyword matching in the full response.
    3. If nothing matches, return NO_SOLUTION.
    """
    text_lower = llm_response.lower()

    # 1. Try explicit recommendation pattern
    pattern = r"recomenda[çc][ãa]o\s*:\s*(.+)"
    match = re.search(pattern, text_lower)
    if match:
        rec_text = match.group(1).strip()
        for tool, keywords in TOOL_KEYWORDS.items():
            if tool == ToolSolution.NO_SOLUTION:
                continue
            for kw in keywords:
                if kw in rec_text:
                    justification = _extract_justification(llm_response, match.end())
                    return ToolRecommendation(tool=tool, justification=justification)
        # Check no-solution keywords in the recommendation line
        for kw in TOOL_KEYWORDS[ToolSolution.NO_SOLUTION]:
            if kw in rec_text:
                return ToolRecommendation(
                    tool=ToolSolution.NO_SOLUTION,
                    justification="Não temos uma solução disponível hoje para esta demanda.",
                )

    # 2. Keyword scan across the full response
    for tool, keywords in TOOL_KEYWORDS.items():
        if tool == ToolSolution.NO_SOLUTION:
            continue
        for kw in keywords:
            if kw in text_lower:
                justification = _extract_justification(llm_response, 0)
                return ToolRecommendation(tool=tool, justification=justification)

    # 3. Check for explicit no-solution phrases
    for kw in TOOL_KEYWORDS[ToolSolution.NO_SOLUTION]:
        if kw in text_lower:
            return ToolRecommendation(
                tool=ToolSolution.NO_SOLUTION,
                justification="Não temos uma solução disponível hoje para esta demanda.",
            )

    # 4. Default: no solution
    return ToolRecommendation(
        tool=ToolSolution.NO_SOLUTION,
        justification="Não foi possível identificar uma ferramenta adequada na resposta.",
    )


def _extract_justification(llm_response: str, start_pos: int) -> str:
    """Extract justification text from the LLM response after the recommendation."""
    remaining = llm_response[start_pos:].strip()
    if remaining:
        # Take up to 500 chars as justification
        return remaining[:500]
    # Fall back to the full response as justification
    return llm_response[:500] if llm_response else "Recomendação baseada na análise do catálogo."
