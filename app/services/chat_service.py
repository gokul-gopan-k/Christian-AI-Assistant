from intent.intent_detector import detect_intent
from safety.safety_rules import check_rules
from retrieval.hybrid import hybrid_search
from retrieval.rerank import reranker
from llm.answer_generator import generate_answer
from verification.citation_verifier import verify_answer


#  Import Short Term Memory + Long Term Persistent Memory items
from memory.short_term_memory import add_message, get_history
from memory.persistent_memory import load_memories, save_memory
from memory.memory_extractor import extract_memory


def answer_question(
    user_id,
    query
):
    #  Safety Check 
    safety_result = check_rules(query)
    if safety_result != "safe":

        return {
            "answer":"I cannot assist with that request.",
            "sources": []
        }
    #  Intent & Retrieval 
    intent = detect_intent(query)

    retrieved = hybrid_search(
        query=query,
        top_k=20
    )

    reranked = reranker(
        query=query,
        retrieved_docs=retrieved,
        top_k=5
    )

    # Append the fresh incoming user message into short term history first
    add_message(user_id, "user", query)
    # Retrieve complete chat history (including the current query)
    history = get_history(user_id)
    # Pull long-term profiling facts about this user from SQLite
    long_term_memories = load_memories(user_id)

    answer = generate_answer(
        query=query,
        retrieved_docs=reranked,
        history=history,
        intent=intent,
        long_term_memories=long_term_memories
    )

    verification = verify_answer(
        query,
        answer,
        reranked
    )

    if verification["supported"] is False:

        answer += (
            "\n\nWarning: confidence is low."
        )

    add_message(
        user_id,
        "user",
        query
    )
    # Append assistant response to short-term context
    add_message(
        user_id,
        "assistant",
        answer
    )

    # Check if this statement contains profile details worth saving long-term
    extracted = extract_memory(query)
    if extracted.get("save") is True and extracted.get("memory"):
        save_memory(user_id, extracted["memory"])

    #  Formatting Sources Output   
    sources = []

    for chunk in reranked:

        sources.append({
            "id": chunk["id"],
            "source": chunk["source"]
        })

    return {
        "answer": answer,
        "sources": sources
    }