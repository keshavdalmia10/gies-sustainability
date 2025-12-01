from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import os
import httpx
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import asyncio

router = APIRouter(
    tags=["news"]
)

class NewsArticle(BaseModel):
    title: str
    description: Optional[str]
    url: str
    source: str
    published_at: Optional[str]
    image_url: Optional[str]
    ai_insight: Optional[str] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticle]

# Cache to store analyzed articles to avoid re-analyzing
# In a real app, use Redis. For MVP, in-memory dict is fine.
# Key: url, Value: ai_insight
insight_cache = {}

# Initialize LLM
# Note: This requires OPENAI_API_KEY to be set in environment
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

async def analyze_article(title: str, description: str) -> str:
    """
    Uses GPT-4o to generate a research opportunity insight from the article.
    """
    try:
        prompt = f"""
        Analyze this news article title and description related to Sustainable Development Goals (SDGs).
        
        Title: {title}
        Description: {description}
        
        Suggest ONE specific research opportunity or project idea for a university student or faculty member based on this news.
        Keep it concise (max 2 sentences). Start with "Research Opportunity:".
        """
        
        messages = [
            SystemMessage(content="You are an academic research advisor specializing in sustainability."),
            HumanMessage(content=prompt)
        ]
        
        response = await llm.ainvoke(messages)
        return response.content
    except Exception as e:
        print(f"Error analyzing article: {e}")
        return "Research Opportunity: Investigate the local impact of this event on community resilience."

@router.get("/sdg", response_model=NewsResponse)
async def get_sdg_news():
    """
    Fetches top SDG-related news and adds AI-generated research insights.
    """
    api_key = os.getenv("NEWS_API_KEY")
    
    articles_data = []
    
    if not api_key:
        print("No NEWS_API_KEY found. Using mock data.")
        # Return Mock Data
        articles_data = [
            {
                "title": "Global Renewable Energy Capacity Hits Record High",
                "description": "The world added 50% more renewable capacity in 2023 than in 2022, with solar PV accounting for three-quarters of additions.",
                "url": "https://example.com/renewable-energy",
                "source": {"name": "Energy News"},
                "publishedAt": "2023-11-15T10:00:00Z",
                "urlToImage": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
            },
            {
                "title": "New AI Model Predicts Climate Patterns with Unprecedented Accuracy",
                "description": "Scientists have developed a machine learning model that outperforms traditional physics-based models in forecasting extreme weather events.",
                "url": "https://example.com/ai-climate",
                "source": {"name": "Tech Daily"},
                "publishedAt": "2023-11-14T14:30:00Z",
                "urlToImage": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
            },
            {
                "title": "Sustainable Urban Farming Initiatives Gain Traction in Major Cities",
                "description": "Vertical farming and rooftop gardens are becoming key components of urban planning to ensure food security and reduce carbon footprints.",
                "url": "https://example.com/urban-farming",
                "source": {"name": "City Life"},
                "publishedAt": "2023-11-13T09:15:00Z",
                "urlToImage": "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
            },
            {
                "title": "Ocean Cleanup Project Removes Record Amount of Plastic",
                "description": "The non-profit organization announced a new milestone in their efforts to clean up the Great Pacific Garbage Patch using advanced technology.",
                "url": "https://example.com/ocean-cleanup",
                "source": {"name": "Ocean Watch"},
                "publishedAt": "2023-11-12T11:45:00Z",
                "urlToImage": "https://images.unsplash.com/photo-1621451537084-482c73073a0f?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
            },
            {
                "title": "Breakthrough in Carbon Capture Technology",
                "description": "Researchers have discovered a new material that can capture carbon dioxide from industrial emissions more efficiently and at a lower cost.",
                "url": "https://example.com/carbon-capture",
                "source": {"name": "Science Today"},
                "publishedAt": "2023-11-11T16:20:00Z",
                "urlToImage": "https://images.unsplash.com/photo-1611273426728-700d071295d5?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3"
            }
        ]
    else:
        # Fetch from NewsAPI
        async with httpx.AsyncClient() as client:
            try:
                print("Fetching news from NewsAPI...")
                response = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": "Sustainable Development Goals OR Climate Action OR Renewable Energy",
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 5,
                        "apiKey": api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
                articles_data = data.get("articles", [])
            except Exception as e:
                print(f"Error fetching news: {e}")
                # Fallback to mock if API fails
                articles_data = []

    # Process articles and add AI insights
    processed_articles = []
    
    # Limit to 5 articles to save tokens/time
    for article in articles_data[:5]:
        url = article.get("url")
        title = article.get("title")
        description = article.get("description") or title
        
        # Check cache
        insight = insight_cache.get(url)
        
        processed_articles.append({
            "title": title,
            "description": description,
            "url": url,
            "source": article.get("source", {}).get("name", "Unknown"),
            "published_at": article.get("publishedAt"),
            "image_url": article.get("urlToImage"),
            "ai_insight": insight # Placeholder, will fill later
        })

    # Concurrently generate insights for missing ones
    tasks = []
    indices_to_update = []
    
    for i, article in enumerate(processed_articles):
        if not article["ai_insight"]:
            tasks.append(analyze_article(article["title"], article["description"]))
            indices_to_update.append(i)
            
    if tasks:
        insights = await asyncio.gather(*tasks)
        for i, insight in zip(indices_to_update, insights):
            processed_articles[i]["ai_insight"] = insight
            insight_cache[processed_articles[i]["url"]] = insight

    return {"articles": processed_articles}
