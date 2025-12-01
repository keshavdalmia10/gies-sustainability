import os
from typing import List, Dict, Any, TypedDict, Annotated
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, literal, or_
from sqlalchemy.orm import selectinload
from app import models, models_networking

# Define State
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    query: str
    extracted_skills: List[str]
    relevant_nodes: List[Dict[str, Any]]
    graph_data: Dict[str, Any]
    final_response: str

# LLM Setup
# Note: This requires OPENAI_API_KEY to be set in environment
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Nodes ---

async def extract_skills(state: AgentState):
    """
    Extracts relevant skills and roles from the user query.
    """
    query = state["query"]
    
    # Hardcoded list of skills for MVP context awareness
    known_skills = [
        "Python", "React", "Data Analysis", "Machine Learning", 
        "Sustainability", "Project Management", "Public Speaking",
        "Java", "C++", "SQL", "Figma", "UI/UX Design"
    ]
    
    system_prompt = f"""You are an expert at analyzing networking requests. 
    Given a user's goal (e.g., "I want to build a mobile app"), identify the key technical and soft skills required.
    
    The database contains these specific skills: {", ".join(known_skills)}.
    Prioritize these exact skill names if they are relevant.
    
    Return ONLY a comma-separated list of skills.
    Example: "Mobile Development, UI/UX Design, React, Project Management"
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    response = await llm.ainvoke(messages)
    skills = [s.strip() for s in response.content.split(",")]
    print(f"DEBUG: Extracted Skills: {skills}")
    
    return {"extracted_skills": skills}

async def retrieve_nodes(state: AgentState, db: AsyncSession):
    """
    Retrieves students and faculty from the database that match the extracted skills.
    """
    skills_list = state["extracted_skills"]
    relevant_nodes = []
    
    # We need to query the DB. Since this is inside the graph, we need the DB session.
    # We'll pass it via config or bind it partially. 
    # For simplicity in this MVP, we might need to inject it or use a helper that gets a fresh session.
    # However, passing 'db' directly to the node function isn't standard LangGraph.
    # We usually pass it in the 'configurable' config.
    
    # For now, let's assume we can search by name for simplicity or use the session passed in context.
    # To make this work with the router, we'll define this as a closure or pass db in state (not serializable though).
    # Better approach: The router runs the graph steps manually or we pass a tool that has access to DB.
    
    # Let's try to find skills in DB that match loosely
    found_skills = []
    for skill_name in skills_list:
        # Bidirectional ILIKE search:
        # 1. DB skill name contains extracted skill (e.g. DB="Python Programming", Query="Python")
        # 2. Extracted skill contains DB skill name (e.g. DB="Python", Query="Python Programming")
        result = await db.execute(
            select(models_networking.Skill)
            .options(
                selectinload(models_networking.Skill.students).selectinload(models_networking.Student.skills),
                selectinload(models_networking.Skill.faculty).selectinload(models.Faculty.skills)
            )
            .where(
                or_(
                    models_networking.Skill.name.ilike(f"%{skill_name}%"),
                    literal(skill_name).ilike(func.concat('%', models_networking.Skill.name, '%'))
                )
            )
        )
        matches = result.scalars().all()
        found_skills.extend(matches)
        
    # Collect people and aggregate their matched skills
    people_map = {} # ID -> {node_data, matched_skills: set()}
    
    for skill in found_skills:
        for s in skill.students:
            s_id = str(s.student_id)
            if s_id not in people_map:
                people_map[s_id] = {
                    "id": s_id,
                    "label": s.name,
                    "type": "student",
                    "all_skills": [sk.name for sk in s.skills], # All skills they have
                    "matched_skills": set(), # Skills relevant to query
                    "group": 1
                }
            people_map[s_id]["matched_skills"].add(skill.name)
                
        for f in skill.faculty:
            f_id = str(f.person_uuid)
            if f_id not in people_map:
                people_map[f_id] = {
                    "id": f_id,
                    "label": f.name,
                    "type": "faculty",
                    "all_skills": [sk.name for sk in f.skills],
                    "matched_skills": set(),
                    "group": 2
                }
            people_map[f_id]["matched_skills"].add(skill.name)
    
    # Convert to list
    for p in people_map.values():
        p["matched_skills"] = list(p["matched_skills"]) # Convert set to list
        relevant_nodes.append(p)
                
    return {"relevant_nodes": relevant_nodes}

def construct_graph(state: AgentState):
    """
    Formats the nodes into a graph structure for the frontend.
    """
    nodes = state["relevant_nodes"]
    edges = []
    
    # Create edges based on shared skills or just connect to a central "Goal" node?
    # Let's connect people who share the same matched skills
    
    # Or better, let's return the nodes and let the frontend visualize them.
    # We can add edges between people and the skills they have.
    
    graph_nodes = []
    graph_edges = []
    
    # Add Skill Nodes
    skill_map = {}
    
    for node in nodes:
        # Add Person Node
        graph_nodes.append({
            "id": node["id"],
            "label": node["label"],
            "type": node["type"],
            "group": node["group"]
        })
        
        # Add Edges to ALL matched skills
        for skill_name in node["matched_skills"]:
            if skill_name not in skill_map:
                skill_id = f"skill_{skill_name}"
                skill_map[skill_name] = skill_id
                graph_nodes.append({
                    "id": skill_id,
                    "label": skill_name,
                    "type": "skill",
                    "group": 3
                })
            
            # Add Edge
            graph_edges.append({
                "source": node["id"],
                "target": skill_map[skill_name]
            })
        
    return {"graph_data": {"nodes": graph_nodes, "edges": graph_edges}}

async def generate_advice(state: AgentState):
    """
    Generates advice on how to connect with these people.
    """
    nodes = state["relevant_nodes"]
    query = state["query"]
    
    if not nodes:
        return {"final_response": "I couldn't find anyone with the exact skills for your request. Try broadening your search or adding more specific skills to the database."}
    
    node_summaries = "\n".join([f"- {n['label']} ({n['type']}): Matches {', '.join(n['matched_skills'])}" for n in nodes[:10]])
    
    system_prompt = """You are a helpful networking advisor. 
    The user wants to achieve a goal, and we have found some relevant people.
    Provide a helpful response suggesting who they should contact and why.
    Be encouraging and specific.
    """
    
    user_content = f"""Goal: {query}
    
    Found People:
    {node_summaries}
    
    (There may be more, but these are the top matches)
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    
    response = await llm.ainvoke(messages)
    return {"final_response": response.content}

# --- Workflow Construction ---

def create_networking_graph(db_session: AsyncSession):
    """
    Creates and compiles the LangGraph workflow, injecting the DB session.
    """
    workflow = StateGraph(AgentState)
    
    # Define wrapper nodes to inject DB
    async def retrieve_nodes_wrapper(state):
        return await retrieve_nodes(state, db_session)
    
    workflow.add_node("extract_skills", extract_skills)
    workflow.add_node("retrieve_nodes", retrieve_nodes_wrapper)
    workflow.add_node("construct_graph", construct_graph)
    workflow.add_node("generate_advice", generate_advice)
    
    workflow.set_entry_point("extract_skills")
    
    workflow.add_edge("extract_skills", "retrieve_nodes")
    workflow.add_edge("retrieve_nodes", "construct_graph")
    workflow.add_edge("construct_graph", "generate_advice")
    workflow.add_edge("generate_advice", END)
    
    return workflow.compile()
