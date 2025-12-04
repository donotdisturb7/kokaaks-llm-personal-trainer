"""
LangChain chains for RAG, context building, and conversational AI.

This module provides pre-configured chains that replace manual
prompt construction and LLM orchestration.
"""

from typing import Optional, Dict, Any
from langchain_core.language_models import BaseChatModel, BaseLLM
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.chains import RetrievalQA
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_postgres import PGVector
import logging

logger = logging.getLogger(__name__)


def create_rag_chain(
    llm: BaseChatModel | BaseLLM,
    vector_store: PGVector,
    search_kwargs: Optional[Dict[str, Any]] = None,
) -> RetrievalQA:
    if search_kwargs is None:
        search_kwargs = {"k": 5}

    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)

    # Custom prompt for RAG that includes instructions about sharecodes
    rag_prompt = PromptTemplate(
        template="""You are an AI assistant specialized in aim training and gaming injury prevention.
You provide advice based on reliable sources and are always cautious with medical recommendations.

CRITICAL - KovaaK's Sharecode Format:
- Sharecodes are LONG alphanumeric codes that appear AFTER the word "Sharecode" in the documents
- Format: "ROUTINE_NAME Sharecode LONGCODE"
- Example: "HAUNTR TRACK Sharecode KOVAAKSCLIPPINGCAFFEINATEDCASH" → sharecode is KOVAAKSCLIPPINGCAFFEINATEDCASH
- The sharecode is what users copy-paste into KovaaK's Playlist tab

CRITICAL INSTRUCTIONS:
- Answer precisely and helpfully based ONLY on the provided context below
- INCLUDE ALL relevant information from the context - do NOT tell users to "check the PDF"
- QUOTE EXACTLY sharecodes, routine names, and instructions without modifying them
- When providing routines, ALWAYS include:
  * The complete sharecode (the long alphanumeric code after "Sharecode")
  * All scenarios/exercises with their exact names and durations
  * Any specific instructions or focus points mentioned
- If the context contains a sharecode, YOU MUST include it in your response
- Do NOT rephrase codes, numbers, or identifiers - copy them exactly as they appear
- If the context doesn't contain sufficient information, say so clearly

Context:
{context}

Question: {question}

Helpful Answer:""",
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": rag_prompt},
    )

    logger.info("Created RAG chain with retriever")
    return chain


def create_context_chain(llm: BaseChatModel | BaseLLM) -> Any:
    context_prompt = ChatPromptTemplate.from_template(
        """You are a specialized aim training coach for KovaaK's FPS Aim Trainer.
You help players improve their accuracy and performance.

USER CONTEXT:

{kovaaks_data}

{local_stats}

{analysis}

INSTRUCTIONS:
- Provide personalized advice based on the user's stats above
- When the user asks for routine recommendations, combine their stats with the training documents
- Suggest specific exercises that target their weak points
- Explain improvement techniques clearly
- Be encouraging but realistic
- Use appropriate technical terms for KovaaK's
- If training documents are provided, prioritize routines that match the user's skill level and weaknesses

Based on this context, you are ready to assist the user with their aim training journey."""
    )

    chain = context_prompt | llm | StrOutputParser()

    logger.info("Created context building chain")
    return chain


def create_conversational_chain(
    llm: BaseChatModel | BaseLLM,
    vector_store: PGVector,
    search_kwargs: Optional[Dict[str, Any]] = None,
    memory: Optional[ConversationBufferMemory] = None,
) -> ConversationalRetrievalChain:
    if search_kwargs is None:
        search_kwargs = {"k": 5}

    if memory is None:
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, output_key="answer"
        )

    retriever = vector_store.as_retriever(search_kwargs=search_kwargs)

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False,
    )

    logger.info("Created conversational chain with memory")
    return chain


def format_context_for_prompt(
    kovaaks_data: Optional[Dict[str, Any]] = None,
    local_stats: Optional[Dict[str, Any]] = None,
    analysis: Optional[Dict[str, Any]] = None,
) -> str:
    parts = []

    if kovaaks_data and "error" not in kovaaks_data:
        scenarios_data = kovaaks_data.get("scenarios_played", {})
        profile = kovaaks_data.get("profile", {})

        scenarios = (
            scenarios_data.get("data", [])
            if isinstance(scenarios_data, dict)
            else scenarios_data
        )

        kovaaks_section = f"""KOVAAK'S API DATA (Live from user account):
- Username: {profile.get("webapp", {}).get("username", "Unknown") if isinstance(profile, dict) else "Unknown"}
- Total scenarios played: {scenarios_data.get("total", len(scenarios)) if isinstance(scenarios_data, dict) else len(scenarios)}

TOP SCENARIOS (by plays):
"""
        for scenario in scenarios[:5]:
            scenario_name = scenario.get(
                "scenarioName", scenario.get("name", "Unknown")
            )
            plays = scenario.get("counts", {}).get("plays", scenario.get("plays", 0))
            best_score = scenario.get("score", scenario.get("highScore", 0))
            kovaaks_section += (
                f"- {scenario_name}: {plays} plays, Best: {best_score:.1f}\n"
            )

        if kovaaks_data.get("recent_scores"):
            kovaaks_section += "\nRECENT HIGH SCORES:\n"
            for score in kovaaks_data["recent_scores"][:3]:
                kovaaks_section += f"- {score.get('scenarioName', 'Unknown')}: {score.get('score', 0):.1f}\n"

        parts.append(kovaaks_section)

    elif local_stats and "error" not in local_stats:
        local_section = f"""LOCAL STATS (recent entries):
- Average score: {local_stats.get("average_score", 0):.1f}
- Total entries: {local_stats.get("total_entries", 0)}
- Recent entries: {local_stats.get("recent_entries", 0)}

TOP SCENARIOS:
"""
        for scenario in local_stats.get("top_scenarios", [])[:5]:
            local_section += f"- {scenario['scenario_name']}: Best score {scenario['best_score']:.1f}, Average {scenario['avg_score']:.1f}, {scenario['plays']} plays\n"

        parts.append(local_section)

    if analysis:
        if analysis.get("strengths"):
            parts.append(f"STRENGTHS: {', '.join(analysis['strengths'])}")

        if analysis.get("weak_points"):
            parts.append(f"AREAS TO IMPROVE: {', '.join(analysis['weak_points'])}")

        if analysis.get("recommendations"):
            parts.append(f"RECOMMENDATIONS: {', '.join(analysis['recommendations'])}")

    return "\n\n".join(parts) if parts else "No context data available"
