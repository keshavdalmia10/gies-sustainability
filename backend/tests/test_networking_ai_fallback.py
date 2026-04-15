import pytest

from app import ai_agent


@pytest.mark.asyncio
async def test_extract_skills_uses_fallback_when_openai_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    ai_agent._llm = None
    ai_agent._llm_unavailable = False

    state = {
        "messages": [],
        "query": "Who knows about Python and SQL?",
        "extracted_skills": [],
        "relevant_nodes": [],
        "graph_data": {},
        "final_response": "",
    }

    result = await ai_agent.extract_skills(state)

    assert "Python" in result["extracted_skills"]
    assert "SQL" in result["extracted_skills"]


@pytest.mark.asyncio
async def test_generate_advice_uses_fallback_when_openai_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    ai_agent._llm = None
    ai_agent._llm_unavailable = False

    state = {
        "messages": [],
        "query": "Who can help with sustainability analytics?",
        "extracted_skills": ["Sustainability", "Data Analysis"],
        "relevant_nodes": [
            {
                "id": "1",
                "label": "Alice Chen",
                "type": "student",
                "all_skills": ["Python", "Data Analysis"],
                "matched_skills": ["Data Analysis"],
                "group": 1,
            }
        ],
        "graph_data": {},
        "final_response": "",
    }

    result = await ai_agent.generate_advice(state)

    assert "Alice Chen" in result["final_response"]
    assert "matches" in result["final_response"].lower() or "strongest" in result["final_response"].lower()
