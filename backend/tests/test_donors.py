from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app

client = TestClient(app)

def test_search_donors():
    # Mock the LLM response
    mock_response_content = """
    {
        "matches": [
            {
                "name": "Gates Foundation",
                "type": "Private Foundation",
                "match_reason": "Focus on global health and water sanitation.",
                "website": "https://www.gatesfoundation.org",
                "contact_info": "info@gatesfoundation.org"
            }
        ]
    }
    """
    
    with patch("app.routers.donors.ChatOpenAI") as MockChat:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value.content = mock_response_content
        MockChat.return_value = mock_llm
        
        # Set dummy key to avoid validation error if mock fails
        import os
        os.environ["OPENAI_API_KEY"] = "dummy"
        
        response = client.post(
            "/api/v1/donors/search",
            json={"project_description": "Water purification project"}
        )
        
        if response.status_code != 200:
            print(f"DEBUG: Response Error: {response.text}")
            
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert len(data["matches"]) == 1
        assert data["matches"][0]["name"] == "Gates Foundation"
