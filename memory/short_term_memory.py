from collections import defaultdict

MAX_HISTORY = 10

conversation_memory = defaultdict(list)


def add_message(user_id, role, content):

    conversation_memory[user_id].append(
        {
            "role": role,
            "content": content
        }
    )

    if len(conversation_memory[user_id]) > MAX_HISTORY:
        conversation_memory[user_id] = \
            conversation_memory[user_id][-MAX_HISTORY:]


def get_history(user_id):

    return conversation_memory[user_id]


def clear_history(user_id):

    conversation_memory[user_id] = []
    