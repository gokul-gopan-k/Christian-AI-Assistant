def recall_at_k(retrieved_ids, relevant_ids):

    relevant = set(relevant_ids)

    found = 0

    for doc_id in retrieved_ids:
        if doc_id in relevant:
            found += 1

    return found / len(relevant)


def precision_at_k(retrieved_ids, relevant_ids):

    relevant = set(relevant_ids)

    found = 0

    for doc_id in retrieved_ids:
        if doc_id in relevant:
            found += 1

    return found / len(retrieved_ids)


def hit_rate(retrieved_ids, relevant_ids):

    relevant = set(relevant_ids)

    for doc_id in retrieved_ids:
        if doc_id in relevant:
            return 1

    return 0