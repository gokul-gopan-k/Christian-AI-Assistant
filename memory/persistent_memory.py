from memory.memory_db import get_connection


def save_memory(user_id, memory_text):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO memories(user_id, memory)
        VALUES (?, ?)
        """,
        (user_id, memory_text)
    )

    conn.commit()
    conn.close()


def load_memories(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT memory
        FROM memories
        WHERE user_id=?
        """,
        (user_id,)
    )

    rows = cur.fetchall()

    conn.close()

    return [r["memory"] for r in rows]