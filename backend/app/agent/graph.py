from typing import TypedDict, List

from langgraph.graph import StateGraph, END

from app.rag.retriever import retrieve
from app.llm.provider import generate
from app.agent.prompts import SYSTEM_PROMPT


class AgentState(TypedDict):
    session_id: str
    message: str
    history: List[dict]
    context: str
    sources: List[str]
    answer: str
    escalated: bool


# Temporary in-memory conversation store.
# Later this can be replaced with Redis/PostgreSQL.
_sessions = {}


def retrieve_node(state: AgentState):

    history_text = ""

    for item in state["history"]:
        history_text += (
            f"Customer: {item['message']}\n"
            f"Agent: {item['answer']}\n"
        )

    retrieval_query = state["message"]

    if history_text:
        retrieval_query = (
            f"Previous conversation:\n"
            f"{history_text}\n"
            f"Current customer question:\n"
            f"{state['message']}"
        )

    results = retrieve(retrieval_query, top_k=3)

    if not results:
        return {
            "context": "",
            "sources": [],
            "escalated": True,
        }

    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"Content: {result['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    sources = list(
        dict.fromkeys(
            result["source"] for result in results
        )
    )

    return {
        "context": context,
        "sources": sources,
        "escalated": False,
    }


def generate_node(state: AgentState):
    # Add conversation history to the question
    history_text = ""

    for item in state["history"]:
        history_text += (
            f"Customer: {item['message']}\n"
            f"Agent: {item['answer']}\n"
        )

    question = state["message"]

    if history_text:
        question = (
            f"Previous conversation:\n"
            f"{history_text}\n"
            f"Current customer message:\n"
            f"{state['message']}"
        )

    result = generate(
        system_prompt=SYSTEM_PROMPT,
        question=question,
        context=state["context"],
    )

    return {
        "answer": result["answer"],
        "escalated": result["escalated"],
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("retrieve")

    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


agent = build_graph()


def run_agent(session_id: str, message: str):

    # Get previous conversation
    history = _sessions.get(session_id, [])

    result = agent.invoke(
        {
            "session_id": session_id,
            "message": message,
            "history": history,
            "context": "",
            "sources": [],
            "answer": "",
            "escalated": False,
        }
    )

    # Save this conversation turn
    history.append(
        {
            "message": message,
            "answer": result["answer"],
        }
    )

    _sessions[session_id] = history

    return result