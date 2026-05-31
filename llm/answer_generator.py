from llm.llm_client import LLMClient
from llm.prompts import (
    SYSTEM_PROMPT,
    ANSWER_TEMPLATE
)


class AnswerGenerator:

    def __init__(self):
        self.llm = LLMClient()

    def build_context(
        self,
        retrieved_docs
    ):

        context_parts = []

        for doc in retrieved_docs:

            chunk = f"""
[{doc['id']}]

Tradition: {doc['tradition']}
Source: {doc['source']}

{doc['content']}
"""

            context_parts.append( chunk.strip() )

        return "\n\n".join( context_parts)

    def build_prompt(
        self,
        question,
        retrieved_docs,
        history, intent, long_term_memories):

        context = self.build_context(retrieved_docs)
    
        # Convert history list into a clean textual string for the LLM
        history_str = ""
        for msg in history:
            history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"

        # Convert long-term memories list into a bulleted profile text block
        memories_str = "\n".join([f"- {m}" for m in long_term_memories]) if long_term_memories else "None"

        prompt = ANSWER_TEMPLATE.format(
            system_prompt=SYSTEM_PROMPT,
            question=question,
            context=context,
            history=history_str.strip(),
            intent=intent,
            user_profile=memories_str.strip()
        )

        return prompt

    def generate_answer(
        self,
        query,
        retrieved_docs,
        history,
        intent,
        long_term_memories
    ):

        prompt = self.build_prompt(
            query,
            retrieved_docs,
            history,
            intent,
            long_term_memories
        )

        answer = self.llm.generate(
            prompt
        )

        return answer
    
#  Create a single instance of the client
_client_instance = AnswerGenerator()

#  Expose the method as a module-level function
generate_answer = _client_instance.generate_answer